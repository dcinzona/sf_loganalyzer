from typing import Type
import sfloganalyzer.Operations.Invocations as OPS
from .Invocations.FatalError import FatalErrorOp
from .LogLine import LogLine
from .Operation import Operation
import sfloganalyzer.options as options


class OperationsList(list["Operation"]):
    def __init__(self, *args, **kwargs):
        super(OperationsList, self).__init__(*args, **kwargs)
        # print(f"{self.__class__.__name__} args: {args}")
        # print(f"{self.__class__.__name__} kwargs: {kwargs}")

    def opsInRange(self, start: int, end: int) -> "OperationsList":
        return [op for op in self if op.lineNumber >= start and op.lineNumber <= end]

    def opsByType(self, opType: Type[Operation]) -> "OperationsList":
        return [op for op in self if isinstance(op, opType)]

    def opsInRangeByType(
        self, start: int, end: int, opType: Type[Operation]
    ) -> "OperationsList":
        return [
            op
            for op in self.opsByType(opType=opType)
            if op.lineNumber >= start and op.lineNumber <= end
        ]

    def clusterOps(self, idx: int = None) -> "OperationsList":
        if idx is None:
            idx = len(self) - 1
        return [op for op in self[:idx] if op.isClusterOp]

    def getOperationClusterId(self, op: Operation) -> str:
        idx = self.index(op)
        clusterOps = self.clusterOps(idx=idx)
        return (
            clusterOps[-1].clusterId if len(clusterOps) > 0 else op.get("clusterId", "")
        )

    def get_idx_from_first_op_or_self(self, input_op: Operation) -> int:
        for op in self:
            if op.uniqueName == input_op.uniqueName:
                return op.idx
        return input_op.idx

    def next_op(self, op: Operation):
        """
        Returns the next operation in the stack
        """
        idx = op.idx
        if idx == len(self) - 1:
            return None
        return self[idx + 1]

    def prev_op(self, op: Operation):
        """
        Returns the previous operation in the stack
        """
        idx = op.idx
        if idx == 0:
            return None
        return self[idx - 1]


class OperationFactory:
    """Manages the operations stack and instantiates the appropriate operation type"""

    OPERATIONS: OperationsList
    hitException: bool = False

    def __init__(self, *args, **kwargs):
        self.OPERATIONS = OperationsList([])
        self.hitException = False
        self.excluded_ops = options.exclude
        # default exclusions until implemented
        self.excluded_ops = (
            *self.excluded_ops,
            *tuple(["dml", "execution", "callout"]),
        )
        self.stop_on_exception = options.stop_on_exception

    def _excluded(self, optype: str):
        return optype in self.excluded_ops

    def generateOperation(self, logLine: LogLine) -> Operation:
        # only push operations onto the stack on operation entry
        # flows need to be handled differently (flow name isn't on the same line as the entry event)
        tokens: list[str] = logLine.lineSplit
        op: Operation = None
        if self.hitException and self.stop_on_exception:
            return None
        if tokens and len(tokens) > 1:
            opType = Operation.getType(tokens)
            if self._excluded(opType):
                return None
            if tokens[1].startswith("METHOD_ENTRY"):
                if len(tokens[-2]) > 0:
                    isCustomMethod = tokens[-1].split(".")[0] not in [
                        "System",
                        "Database",
                        "UserInfo",
                    ]
                    if isCustomMethod:
                        op = OPS.MethodOperation(logLine)
                        op = OPS.MethodOperation.METHODSTACK.pop()
                        op.finished = True
            elif tokens[1].startswith("DML_"):
                op = OPS.DMLOperation(logLine)
            elif tokens[1].startswith("EXECUTION_"):
                op = OPS.ExecutionOperation(logLine)
            elif tokens[1].startswith("CALLOUT"):
                op = OPS.CalloutOperation(logLine)
            elif tokens[1].startswith("FLOW_"):
                if tokens[1] in [
                    "FLOW_CREATE_INTERVIEW_BEGIN",
                    "FLOW_CREATE_INTERVIEW_END",
                ]:
                    op = OPS.FlowOperation(logLine)
                    op.finished = False
                    if op.operationAction == "FLOW_CREATE_INTERVIEW_END":
                        op = OPS.FlowOperation.FLOWSTACK.pop()
                        op.finished = True
            elif tokens[1].startswith("CODE_UNIT_STARTED"):
                # Check if this is a trigger
                last: str = tokens[-1]
                if last == "TRIGGERS":
                    # this is a generic line that specifies that triggers are running (probably to group them all together)
                    return None
                elif opType == "trigger":
                    op = OPS.TriggerOperation(logLine)
                    op = OPS.TriggerOperation.TRIGGERSTACK.pop()
                    op.finished = True
                elif opType == "flow":
                    op = OPS.FlowOperation(logLine)
                    op.finished = False
                elif opType == "workflow":
                    pass
                elif opType == "validation":
                    pass
                elif opType == "duplicateDetector":
                    pass
                elif opType == "system":
                    pass
                elif opType == "apex":
                    op = OPS.MethodOperation(logLine)
                    op = OPS.MethodOperation.METHODSTACK.pop()
                    op.finished = True
                    pass
            elif tokens[1] in ["FATAL_ERROR", "EXCEPTION_THROWN"]:
                self.hitException = True
                op = FatalErrorOp(logLine)
                op.finished = True
                if op.uniqueName == self.OPERATIONS[-1].uniqueName:
                    return op  # don't append to the stack since this is probably a duplicate

            if op is not None and op.finished:
                op.idx = len(self.OPERATIONS)
                idx = self.OPERATIONS.get_idx_from_first_op_or_self(op)
                op._nodeId = f"{op.__class__.__name__}({idx+1})"
                self.appendToStack(op)
                return op

    def getOpenParentOperation(self, opIn: Operation):
        if len(self.OPERATIONS) == 0:
            return None
        for op in self.OPERATIONS[::-1]:
            if op.get("finished", False) is False and op.eventId != opIn.eventId:
                return op
        return None

    def appendToStack(self, op: Operation):
        """Every time we add an operation to the stack, set the previous operation and the next operation
           PrevOp <- op -> NextOp
        Args:
            op (Operation): The operation to add to the stack
        """
        if len(self.OPERATIONS) > 0:
            op.PREV_OPERATION = self.OPERATIONS[-1]
            op.PREV_OPERATION.NEXT_OPERATION = op
        self.OPERATIONS.append(op)

    def getLastOperationOfType(self, opType: Type):
        for op in reversed(self.OPERATIONS):
            if op.__class__ == opType:
                return op
        return None

    def getLastOperationByName(self, name: str):
        for op in reversed(self.OPERATIONS):
            if op.name == name:
                return op
        return None
