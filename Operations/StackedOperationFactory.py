from Operations.EntryOrExit import EntryOrExit
import Operations.Invocations as OP
from Operations.Operation import Operation
from Operations.OperationFactory import OperationFactory


class StackedOperationFactory(OperationFactory):
    """Manages the operations stack and instantiates the appropriate operation type"""

    OPERATIONS: list[Operation] = []
    hitException: bool = False

    def __init__(self, *args, **kwargs):
        super(StackedOperationFactory, self).__init__(*args, **kwargs)
        self.OPERATIONS = []
        self.hitException = False
        self.excluded_ops = kwargs.get("exclude", ())
        # default exclusions until implemented
        self.excluded_ops = (
            *self.excluded_ops,
            *tuple(["dml", "execution", "callout"]),
        )
        self.stop_on_exception = kwargs.get("stop-on-exception", False)

    def createStackedOperation(self, logLine):
        """No longer used at the render results weren't as expected.
        While operations (log events) are stacked and nested, the purpose
        of this application is to visualize the order of operations, sequentially.
        So, stacking is not needed.
        """
        tokens: list[str] = logLine.line.split("|")
        operation = None
        if self.hitException and self.stop_on_exception:
            return None
        if tokens and len(tokens) > 1:
            opType = Operation.getType(tokens)
            if tokens[1].startswith("METHOD_") and self._shouldProcess(opType):
                if len(tokens[-2]) > 0:
                    # Second to last token is the method line number
                    operation = OP.MethodOperation(logLine)
                    pass
            elif tokens[1].startswith("DML_") and self._shouldProcess(opType):
                pass
                # operation = DMLOperation(logLine);
            elif tokens[1].startswith("EXECUTION_") and self._shouldProcess(opType):
                pass
                # operation = ExecutionOperation(tokens, logLine.lineNumber);
            elif tokens[1].startswith("CALLOUT") and self._shouldProcess(opType):
                operation = OP.CalloutOperation(logLine)
            elif tokens[1].startswith("FLOW_") and self._shouldProcess(opType):
                if tokens[1] in EntryOrExit.ALL:
                    operation = OP.FlowOperation(logLine)
            elif tokens[1].startswith("CODE_UNIT_") and self._shouldProcess(opType):
                # Check if this is a trigger
                if opType == "triggers":
                    operation = OP.TriggerOperation(logLine)
                elif opType == "flows":
                    operation = OP.FlowOperation(logLine)
                elif opType == "workflows":
                    pass
                elif opType == "validations":
                    pass
                elif opType == "duplicateDetector":
                    pass
                elif opType == "apex":
                    operation = OP.MethodOperation(logLine)
                    pass
            elif tokens[1] in ["FATAL_ERROR", "EXCEPTION_THROWN"]:
                self.hitException = True
                operation = OP.FatalErrorOp(logLine)
                if self.findInStack(operation) is None:
                    lastOp = self.getOpenParentOperation(operation)
                    if lastOp is not None:
                        operation.parent = (
                            lastOp
                            if operation.get("parent", None) is None
                            else operation.parent
                        )
                return operation

        # The operation here is based on the log line, so it may already be in the stack
        if operation is not None:
            if operation.get("parent", None) is None and operation.isEntry():
                operation.parent = self.getOpenParentOperation(operation)
            operation.tokens = tokens
            if (
                isinstance(operation, OP.FlowOperation)
                and operation.eventType == "FLOW_WRAPPER"
            ):
                operation = None
                return None
            op = self.findInStack(operation)
            if op is not None:
                op.update(operation.__dict__)
        return operation
