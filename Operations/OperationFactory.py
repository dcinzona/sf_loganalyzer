from pickle import STACK_GLOBAL
from pprint import pp
from typing import Type
from Operations.EntryOrExit import EntryOrExit
from Operations.Invocations.FatalError import FatalErrorOp
from Operations.LogLine import LogLine
from Operations.Operation import Operation
from Operations.Invocations.CalloutOperation import CalloutOperation
from Operations.Invocations.DMLOperation import DMLOperation
from Operations.Invocations.ExecutionOperation import ExecutionOperation
from Operations.Invocations.FlowOperation import FlowOperation
from Operations.Invocations.MethodOperation import MethodOperation
from Operations.Invocations.TriggerOperation import TriggerOperation


class OperationFactory():
    OPERATIONS: list[Operation] = []
    hitException: bool = False

    def __init__(self, *args, **kwargs):
        self.OPERATIONS = []
        self.hitException = False
        self.excluded_ops = kwargs.get('exclude', [])
        self.stop_on_exception = kwargs.get('stop-on-exception', False)

    def _excluded(self, optype: str):
        return optype in self.excluded_ops

    def createOperation(self, logLine):
        tokens: list[str] = logLine.line.split("|")
        operation = None
        if(self.hitException == True and self.stop_on_exception):
            return None
        if(tokens and len(tokens) > 1):
            opType = Operation.getType(tokens)
            if(tokens[1].startswith("METHOD_") and self._shouldProcess(opType)):
                if(len(tokens[-2]) > 0):
                    # Second to last token is the method line number
                    operation = MethodOperation(logLine)
                    pass
            elif(tokens[1].startswith("DML_") and self._shouldProcess(opType)):
                pass
                # operation = DMLOperation(logLine);
            elif(tokens[1].startswith("EXECUTION_") and self._shouldProcess(opType)):
                pass
                # operation = ExecutionOperation(tokens, logLine.lineNumber);
            elif(tokens[1].startswith("CALLOUT") and self._shouldProcess(opType)):
                operation = CalloutOperation(logLine)
            elif(tokens[1].startswith("FLOW_") and self._shouldProcess(opType)):
                if(tokens[1] in EntryOrExit.ALL):
                    operation = FlowOperation(logLine)
            elif(tokens[1].startswith("CODE_UNIT_") and self._shouldProcess(opType)):
                # Check if this is a trigger
                last: str = tokens[-1]
                if(opType == 'triggers'):
                    operation = TriggerOperation(logLine)
                elif(opType == 'flows'):
                    operation = FlowOperation(logLine)
                elif(opType == 'workflows'):
                    pass
                elif(opType == 'validations'):
                    pass
                elif(opType == 'duplicateDetector'):
                    pass
                elif(opType == 'apex'):
                    operation = MethodOperation(logLine)
                    pass
            elif(tokens[1] in ['FATAL_ERROR', 'EXCEPTION_THROWN']):
                self.hitException = True
                operation = FatalErrorOp(logLine)
                if(self.findInStack(operation) is None):
                    lastOp = self.getOpenParentOperation(operation)
                    if(lastOp is not None):
                        operation.parent = lastOp if operation.get(
                            'parent', None) is None else operation.parent
                return operation

        # The operation here is based on the log line, so it may already be in the stack
        if(operation is not None):
            if(operation.get('parent', None) == None and operation.isEntry()):
                operation.parent = self.getOpenParentOperation(operation)
            operation.tokens = tokens
            if(isinstance(operation, FlowOperation) and operation.eventType == 'FLOW_WRAPPER'):
                operation = None
                return None
            op = self.findInStack(operation)
            if(op is not None):
                op.update(operation.__dict__)
        return operation

    def createOrderedOperation(self, logLine: LogLine):
        # only push operations onto the stack on operation entry
        # flows need to be handled differently (flow name isn't on the same line as the entry event)
        tokens: list[str] = logLine.lineSplit
        op: Operation = None
        if(self.hitException == True and self.stop_on_exception):
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
                        op = MethodOperation(logLine)
                        op = MethodOperation.METHODSTACK.pop()
                        op.finished = True
            elif(tokens[1].startswith("DML_")):
                pass
                #op = DMLOperation(logLine)
            elif(tokens[1].startswith("EXECUTION_")):
                pass
                #op = ExecutionOperation(logLine)
            elif(tokens[1].startswith("CALLOUT")):
                pass
                #op = CalloutOperation(logLine)
            elif(tokens[1].startswith("FLOW_")):
                if(tokens[1] in ['FLOW_CREATE_INTERVIEW_BEGIN', 'FLOW_CREATE_INTERVIEW_END']):
                    op = FlowOperation(logLine)
                    op.finished = False
                    if(op.operationAction == 'FLOW_CREATE_INTERVIEW_END'):
                        op = FlowOperation.FLOWSTACK.pop()
                        op.finished = True
            elif(tokens[1].startswith("CODE_UNIT_STARTED")):
                # Check if this is a trigger
                last: str = tokens[-1]
                if(last == 'TRIGGERS'):
                    # this is a generic line that specifies that triggers are running (probably to group them all together)
                    return None
                elif(opType == 'trigger'):
                    op = TriggerOperation(logLine)
                    op = TriggerOperation.TRIGGERSTACK.pop()
                    op.finished = True
                elif(opType == 'flow'):
                    op = FlowOperation(logLine)
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
                    op = MethodOperation(logLine)
                    op = MethodOperation.METHODSTACK.pop()
                    op.finished = True
                    pass
            elif(tokens[1] in ['FATAL_ERROR', 'EXCEPTION_THROWN']):
                self.hitException = True
                op = FatalErrorOp(logLine)
                op.finished = True

            prev = self.OPERATIONS[-1] if len(self.OPERATIONS) > 0 else None
            if(op is not None and op.finished):
                if(op.get('parent', None) == None and prev is not None):
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
            if(op.get('finished', False) == False and op.eventId != opIn.eventId):
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
            elif(isinstance(op, FlowOperation) == False):
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

        Args:
            op (Operation): The operation to add to the stack
        """
        if(len(self.OPERATIONS) > 0):
            op.PREV_OPERATION = self.OPERATIONS[-1]
            if(op.PREV_OPERATION is not None):
                op.PREV_OPERATION.NEXT_OPERATION = op
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
