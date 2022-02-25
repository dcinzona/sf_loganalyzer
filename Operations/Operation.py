
from pprint import pp
import traceback
from Operations.EntryOrExit import EntryOrExit, EntryPoints, ExitPoints
from Operations.OpUtils import dynamicDict
from Operations.LogLine import LogLine


class kLimit:
    value: int = 0
    maxValue: int = 0

    def __init__(self, val, maxVal):
        self.value = val
        self.maxValue = maxVal


class LimitData(dict):
    def __init__(self, initializer: dict = None):
        if(initializer is not None):
            super().__init__(initializer)
        else:
            self['startlimits'] = {}
            self['endlimits'] = {}

    def addLimit(self, start: bool, key: str, val: dict):
        if(start):
            self['startlimits'].setdefault(key, val)
            #self['startlimits'][key] = val
        else:
            self['endlimits'].setdefault(key, val)
            #self['endlimits'][key] = val


class Operation(dynamicDict):
    # instance properties
    name: str = ''
    lineNumber: int = 0
    timeStamp: str = None
    eventType: str = None
    eventId: str = None
    eventSubType: str = None
    operationAction: str = ''
    finished: bool = False
    namespace = '(default)'
    limitsProcessed = 0
    LIMIT_USAGE_FOR_NS = []
    PREV_OPERATION: 'Operation' = None
    NEXT_OPERATION: 'Operation' = None

    # static properties
    REDACT: bool = False

    def __init__(self, *args, **kwargs):
        super(dynamicDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

    def __init__(self, ll: dict):
        super(Operation, self).__init__(ll)

    def __init__(self, ll: LogLine):
        tokens = ll.lineSplit
        self.operationAction = tokens[1]
        self.lineNumber = ll.lineNumber
        self.ll = ll
        self.timeStamp = tokens[0] if self.timeStamp is None else self.timeStamp
        if(self.operationAction in [EntryPoints.CODE_UNIT_STARTED]):
            self.clusterNode = True
        elif(self.get('clusterNode', False) != True):
            self.clusterNode = False
        super(Operation, self).__init__(self.__dict__)

    def __str__(self):
        obj: dict = {}
        for k, v in self.items():
            if(k not in ['parent', 'children', 'll']):
                if(k == 'LIMIT_USAGE_FOR_NS'):
                    obj[k] = len(v)
                else:
                    obj[k] = v if not isinstance(
                        v, dynamicDict) else {v.__class__.__name__: f'[{v.lineNumber}] {v.eventId}'}
        return obj.__repr__()

    @property
    def safeName(self):
        if(Operation.REDACT):
            return self.nodeId
        escStr = self.name.replace('<', '&lt;').replace('>', '&gt;')
        return escStr.split(':')[0] if ':' in escStr and not escStr.startswith('apex:') else escStr

    @property
    def isClusterOp(self) -> bool:
        """When a Code Unit has LIMIT_USAGE_FOR_NS data, it is a cluster operation

        Returns:
            bool: Whether the operation represents a cluster of operations
        """
        return len(self.get('LIMIT_USAGE_FOR_NS', [])) > 0

    # should be implemented by subclasses
    def processLimits(self, logline: LogLine):
        if(logline.additionalLines is not None and len(logline.additionalLines) > 0):
            namespace = logline.lineSplit[-2]
            if(namespace == self.namespace):
                self.LIMIT_USAGE_FOR_NS = logline.additionalLines

    def isEntry(self):
        if(self.get('eventId', '').startswith('ERROR|')):
            return True
        return self.operationAction in [EntryPoints.CODE_UNIT_STARTED, ExitPoints.FLOW_CREATE_INTERVIEW_END, EntryPoints.METHOD_ENTRY]

    def isExit(self):
        return self.operationAction in ExitPoints.EXIT_POINTS

    def appendTo(self, opStack: list):
        opStack.append(self)

    @staticmethod
    def getType(tokens: list[str] = None):
        if(tokens is None):
            return None
        evnt: str = tokens[1]
        last: str = tokens[-1].split('.')[0]
        if(evnt.startswith('METHOD_')):
            return 'apex'
        elif(evnt.startswith('FLOW_')):
            return 'flow'
        elif(evnt.startswith('SOQL_')):
            return 'soql'
        elif(evnt.startswith('CALLOUT_')):
            return 'callout'
        elif(evnt.startswith('DML_')):
            return 'dml'
        elif(evnt.startswith('CODE_UNIT_')):
            if(last.startswith("__sfdc_trigger")):
                return 'trigger'
            elif(last.startswith('Workflow:')):
                return 'workflow'
            elif(last.startswith('Flow:')):
                return 'flow'
            elif(last.startswith("Validation:")):
                return 'validation'
            elif(last.startswith("DuplicateDetector")):
                return 'duplicateDetector'
            elif(last.lower() not in ['system', 'database', 'userInfo']):
                return 'apex'
        elif(evnt in ['FATAL_ERROR', 'EXCEPTION_THROWN']):
            # return 'exceptions'
            return ''  # always display errors / exceptions
        return 'Unknown'

    # @staticmethod
    # def findSelfinStack(op, stack:list[dict], eventIdOnly=False) -> dict:
    #     if(len(stack) > 0):
    #         for i in range(len(stack)-1, -1, -1):
    #             sop = stack[i]
    #             if(sop.get('eventId') == op.eventId):
    #                 return stack.pop(i)
    #             if(eventIdOnly == False):
    #                 try:
    #                     if(sop.get('name') == op.name and sop.get('eventType') == op.eventType, sop.get('eventSubType') == op.eventSubType):
    #                         return stack.pop(i)
    #                     # if(sop.eventType == op.eventType and sop.eventSubType == op.eventSubType):
    #                     #     return sop,i
    #                 except Exception:
    #                     print(traceback.format_exc())
    #                     print(op)
    #                     pp(stack[i])
    #                     exit()
    #     print(f'{op.name} not found in stack :(')
    #     pp(stack)
    #     pp(op)
    #     return None
