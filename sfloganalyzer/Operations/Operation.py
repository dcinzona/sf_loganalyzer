import base64
import pprint
from .EntryOrExit import EntryPoints, ExitPoints
from .OpUtils import dynamicDict
from .LogLine import LogLine
from pprint import pformat
import sfloganalyzer.options as options


class kLimit:
    value: int = 0
    maxValue: int = 0

    def __init__(self, val, maxVal):
        self.value = val
        self.maxValue = maxVal


class LimitData(dict):
    """Used for flow limit tracking - still under development

    Args:
        dict (_type_): TBD
    """

    def __init__(self, initializer: dict = None):
        if initializer is not None:
            super().__init__(initializer)
        else:
            self["startlimits"] = {}
            self["endlimits"] = {}

    def addLimit(self, start: bool, key: str, val: dict):
        if start:
            self["startlimits"].setdefault(key, val)
            # self['startlimits'][key] = val
        else:
            self["endlimits"].setdefault(key, val)
            # self['endlimits'][key] = val


class Operation(dynamicDict):
    """The core base class for all operations.  Extensable by subclasses.

    Args:
        dynamicDict (_type_): Usually initiated with a LogLine object, but this may change

    Returns:
        _type_: Subclass of dynamicDict
    """

    # instance properties
    name: str = ""
    lineNumber: int = 0
    timeStamp: str = None
    eventType: str = None
    eventId: str = None
    eventSubType: str = None
    operationAction: str = ""
    finished: bool = False
    namespace = "(default)"
    limitsProcessed = 0
    LIMIT_USAGE_FOR_NS = []
    PREV_OPERATION: "Operation" = None
    NEXT_OPERATION: "Operation" = None
    color = "#FFFFFF"
    idx: int = 0

    @property
    def idx_label(self) -> str:
        return f"{self.idx + 1}"

    # def __init__(self, *args, **kwargs):
    #     super(dynamicDict, self).__init__(*args, **kwargs)
    #     self.__dict__ = self
    #     raise Exception(f'{self.__class__.__name__} is an abstract class')

    def clone(self) -> "Operation":
        op = dynamicDict(self.__dict__)
        op.__dict__ = self.__dict__
        op.__class__ = self.__class__
        return op

    def __init__(self, ll: LogLine):
        tokens = ll.lineSplit
        self.operationAction = tokens[1]
        self.lineNumber = ll.lineNumber
        self.ll = ll
        self.timeStamp = tokens[0] if self.timeStamp is None else self.timeStamp
        if self.operationAction in [EntryPoints.CODE_UNIT_STARTED]:
            self.clusterNode = True
        elif self.get("clusterNode", False) is not True:
            self.clusterNode = False
        super(Operation, self).__init__(self.__dict__)

    def toDict(self):
        obj: dict = {}
        skipProps = ["parent", "children", "lineNumber", "line", "lineSplit", "cluster"]
        for k, v in self.items():
            if k not in skipProps:
                if k == "LIMIT_USAGE_FOR_NS":
                    obj[k] = len(v)
                elif k == "_nodeId":
                    obj["nodeId"] = self.nodeId
                elif k == "ll":
                    obj["logline"] = f"[{self.lineNumber}] {v.line}"
                elif isinstance(v, Operation):
                    obj[k] = {v.__class__.__name__: f"[{v.lineNumber}] {v.eventId}"}
                else:
                    obj[k] = v  # type(v)
        return obj

    def __str__(self):
        # return pformat(vars(obj), indent=4, width=1)
        return f"{self.__class__.__name__}({pformat(self.toDict(), indent=4, width=1)})"

    @property
    def safeName(self):
        """Returns the operation name stripped of excess data and unsafe rendering characters
           Also checks for the redaction flag and returns a redacted unique name of the operation


        Returns:
            _type_: _description_
        """
        if options.redact:
            return self.nodeId
        escStr = self.name.replace("<", "&lt;").replace(">", "&gt;")
        # some exceptions will have too much detail after the first ':' so we strip after the first ':'
        # invoked actions can start with apex:// so we want to keep those
        return (
            escStr.split(":")[0]
            if ":" in escStr and not escStr.startswith("apex:")
            else escStr
        )

    @property
    def isClusterOp(self) -> bool:
        """When a Code Unit has LIMIT_USAGE_FOR_NS data, it is a cluster operation

        Returns:
            bool: Whether the operation represents a cluster of operations
        """
        return len(self.get("LIMIT_USAGE_FOR_NS", [])) > 0

    # should be implemented by subclasses
    def processLimits(self, logline: LogLine):
        if logline.additionalLines is not None and len(logline.additionalLines) > 0:

            namespace = logline.lineSplit[-2]
            if namespace == self.namespace:
                self.LIMIT_USAGE_FOR_NS = logline.additionalLines

    def isEntry(self):
        if self.get("eventId", "").startswith("ERROR|"):
            return True
        return self.operationAction in [
            EntryPoints.CODE_UNIT_STARTED,
            ExitPoints.FLOW_CREATE_INTERVIEW_END,
            EntryPoints.METHOD_ENTRY,
        ]

    def isExit(self):
        return self.operationAction in ExitPoints.EXIT_POINTS

    def appendTo(self, opStack: list):
        opStack.append(self)

    @staticmethod
    def getType(tokens: list[str] = None):
        if tokens is None:
            return None
        evnt: str = tokens[1]
        last: str = tokens[-1].split(".")[0]
        if evnt.startswith("METHOD_"):
            return "apex"
        elif evnt.startswith("FLOW_"):
            return "flow"
        elif evnt.startswith("SOQL_"):
            return "soql"
        elif evnt.startswith("CALLOUT_"):
            return "callout"
        elif evnt.startswith("DML_"):
            return "dml"
        elif evnt.startswith("CODE_UNIT_"):
            if last.startswith("__sfdc_trigger"):
                return "trigger"
            elif last.startswith("Workflow:"):
                return "workflow"
            elif last.startswith("Flow:"):
                return "flow"
            elif last.startswith("Validation:"):
                return "validation"
            elif last.startswith("DuplicateDetector"):
                return "duplicateDetector"
            elif last.lower() not in ["system", "database", "userInfo"]:
                return "apex"
        elif evnt in ["FATAL_ERROR", "EXCEPTION_THROWN"]:
            # return 'exceptions'
            return ""  # always display errors / exceptions
        return "Unknown"

    @classmethod
    def print(cls):
        cp = cls.__dict__.copy()
        if "parent" in cp:
            cp.pop("parent")
        if "tokens" in cp:
            cp.pop("tokens")
        if "lineSplit" in cp:
            cp.pop("lineSplit")
        pprint.pp(cp)

    @property
    def nodeId(self):
        if self.get("_nodeId", None) is None:
            name = self.uniqueName
            self._nodeId = base64.b64encode(name.encode("utf-8")).decode("utf-8")
        return self._nodeId

    @property
    def uniqueName(self) -> str:
        return f"{self.eventType}|{self.name}"
