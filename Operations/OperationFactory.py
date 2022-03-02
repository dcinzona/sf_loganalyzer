from pprint import pp
from typing import Type
import Operations.Invocations as OPS
from Operations.Invocations.FatalError import FatalErrorOp
from Operations.LogLine import LogLine
from Operations.Operation import Operation


class OperationsList(list['Operation']):
    def __init__(self, *args, **kwargs):
        super(OperationsList, self).__init__(*args, **kwargs)
        print(f'{self.__class__.__name__} args: {args}')
        print(f'{self.__class__.__name__} kwargs: {kwargs}')

    def opsInRange(self, start: int, end: int) -> 'OperationsList':
        return [op for op in self if op.lineNumber >= start and op.lineNumber <= end]

    def opsByType(self, opType: Type[Operation]) -> 'OperationsList':
        return [op for op in self if isinstance(op, opType)]

    def opsInRangeByType(self, start: int, end: int, opType: Type[Operation]) -> 'OperationsList':
        return [op for op in self.opsByType(opType=opType) if op.lineNumber >= start and op.lineNumber <= end]

    def clusterOps(self, idx: int = None) -> 'OperationsList':
        if(idx is None):
            idx = len(self) - 1
        return [op for op in self[:idx] if op.isClusterOp]

    def getOperationClusterId(self, op: Operation) -> str:
        idx = self.index(op)
        clusterOps = self.clusterOps(idx=idx)
        return clusterOps[-1].clusterId if len(clusterOps) > 0 \
            else op.get('clusterId', '')


class OperationFactory():
    """Manages the operations stack and instantiates the appropriate operation type"""
    OPERATIONS: OperationsList
    hitException: bool = False

    def __init__(self, *args, **kwargs):
        self.OPERATIONS = OperationsList([])
        self.hitException = False
        self.excluded_ops = kwargs.get(
            'exclude', ())
        # default exclusions until implemented
        self.excluded_ops = (*self.excluded_ops, *tuple(
            ["dml", "execution", "callout"]))
        self.stop_on_exception = kwargs.get('stop-on-exception', False)

    def _excluded(self, optype: str):
        return optype in self.excluded_ops

    def generateOperation(self, logLine: LogLine) -> Operation:
        # only push operations onto the stack on operation entry
        # flows need to be handled differently (flow name isn't on the same line as the entry event)
        tokens: list[str] = logLine.lineSplit
        op: Operation = None
        if(self.hitException and self.stop_on_exception):
            return None
        if(tokens and len(tokens) > 1):
            opType = Operation.getType(tokens)
            if(self._excluded(opType)):
                return None
            if(tokens[1].startswith("METHOD_ENTRY")):
                if(len(tokens[-2]) > 0):
                    isCustomMethod = tokens[-1].split('.')[0] not in [
                        'System', 'Database', 'UserInfo']
                    if(isCustomMethod):
                        op = OPS.MethodOperation(logLine)
                        op = OPS.MethodOperation.METHODSTACK.pop()
                        op.finished = True
            elif(tokens[1].startswith("DML_")):
                op = OPS.DMLOperation(logLine)
            elif(tokens[1].startswith("EXECUTION_")):
                op = OPS.ExecutionOperation(logLine)
            elif(tokens[1].startswith("CALLOUT")):
                op = OPS.CalloutOperation(logLine)
            elif(tokens[1].startswith("FLOW_")):
                if(tokens[1] in ['FLOW_CREATE_INTERVIEW_BEGIN', 'FLOW_CREATE_INTERVIEW_END']):
                    op = OPS.FlowOperation(logLine)
                    op.finished = False
                    if(op.operationAction == 'FLOW_CREATE_INTERVIEW_END'):
                        op = OPS.FlowOperation.FLOWSTACK.pop()
                        op.finished = True
            elif(tokens[1].startswith("CODE_UNIT_STARTED")):
                # Check if this is a trigger
                last: str = tokens[-1]
                if(last == 'TRIGGERS'):
                    # this is a generic line that specifies that triggers are running (probably to group them all together)
                    return None
                elif(opType == 'trigger'):
                    op = OPS.TriggerOperation(logLine)
                    op = OPS.TriggerOperation.TRIGGERSTACK.pop()
                    op.finished = True
                elif(opType == 'flow'):
                    op = OPS.FlowOperation(logLine)
                    op.finished = False
                elif(opType == 'workflow'):
                    pass
                elif(opType == 'validation'):
                    pass
                elif(opType == 'duplicateDetector'):
                    pass
                elif(opType == 'system'):
                    pass
                elif(opType == 'apex'):
                    op = OPS.MethodOperation(logLine)
                    op = OPS.MethodOperation.METHODSTACK.pop()
                    op.finished = True
                    pass
            elif(tokens[1] in ['FATAL_ERROR', 'EXCEPTION_THROWN']):
                self.hitException = True
                op = FatalErrorOp(logLine)
                op.finished = True

            prev = self.OPERATIONS[-1] if len(self.OPERATIONS) > 0 else None
            if(op is not None and op.finished):
                if(op.get('parent', None) is None and prev is not None):
                    if(prev.eventId == op.eventId):
                        return None
                    op.parent = prev
                else:
                    op.parent = None

                self.appendToStack(op)
                return op

    def getOpenParentOperation(self, opIn: Operation):
        if(len(self.OPERATIONS) == 0):
            return None
        for op in self.OPERATIONS[::-1]:
            if(op.get('finished', False) is False and op.eventId != opIn.eventId):
                return op
        return None

    def findInStack(self, op: Operation) -> Operation:
        if(len(self.OPERATIONS) == 0):
            self.appendToStack(op)
            return op
        # loop through the stack backwards
        for stackOp in self.OPERATIONS[::-1]:
            if(stackOp.eventId == op.eventId):
                stackOp.update(op.__dict__)
                return op
            elif(isinstance(op, OPS.FlowOperation) is False):
                try:
                    if(stackOp.name == op.name and stackOp.eventType == op.eventType and stackOp.eventSubType == op.eventSubType):
                        stackOp.update(op.__dict__)
                        return op
                except Exception as e:
                    pp(op)
                    pp(stackOp)
                    raise e
        # wasn't found in the stack so add it
        self.appendToStack(op)
        return None

    def appendToStack(self, op: Operation):
        """Every time we add an operation to the stack, set the previous operation and the next operation
           PrevOp <- op -> NextOp
        Args:
            op (Operation): The operation to add to the stack
        """
        if(len(self.OPERATIONS) > 0):
            # op.PREV_OPERATION = self.OPERATIONS[-1]
            # self.OPERATIONS[-1].NEXT_OPERATION = op
            pass
        self.OPERATIONS.append(op)

    def getLastOperationOfType(self, opType: Type):
        for op in reversed(self.OPERATIONS):
            if(op.__class__ == opType):
                return op
        return None

    def getLastOperationByName(self, name: str):
        for op in reversed(self.OPERATIONS):
            if(op.name == name):
                return op
        return None
