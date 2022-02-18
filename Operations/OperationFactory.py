from pickle import STACK_GLOBAL
from pprint import pp
from Operations.EntryOrExit import EntryOrExit
from Operations.Invocations.FatalError import FatalErrorOp
from Operations.Operation import Operation
from Operations.Invocations.CalloutOperation import CalloutOperation
from Operations.Invocations.DMLOperation import DMLOperation
from Operations.Invocations.ExecutionOperation import ExecutionOperation
from Operations.Invocations.FlowOperation import FlowOperation
from Operations.Invocations.MethodOperation import MethodOperation
from Operations.Invocations.TriggerOperation import TriggerOperation
from Operations.OperationStack import OperationStack

class OperationFactory():
    OPERATIONS:list[Operation] = []

    def __init__(self, *args, **kwargs):
        self.OPERATIONS = []
        pass

    def createOperation(self, logLine):
        tokens:list[str]  = logLine.line.split("|");
        operation = None
        if(tokens and len(tokens)>1):
            if(tokens[1].startswith("METHOD_")):
                if(len(tokens[-2]) > 0):
                    # Second to last token is the method line number
                    operation = MethodOperation(logLine)
                    pass
            elif(tokens[1].startswith("DML_")):
                pass
                # operation = DMLOperation(logLine);
            elif(tokens[1].startswith("EXECUTION_")):
                pass
                # operation = ExecutionOperation(tokens, logLine.lineNumber);
            elif(tokens[1].startswith("CALLOUT")):
                operation = CalloutOperation(logLine);
            elif(tokens[1].startswith("FLOW_")):
                if(tokens[1] in EntryOrExit.ALL):
                    operation = FlowOperation(logLine);
            elif(tokens[1].startswith("CODE_UNIT_")):
                #Check if this is a trigger
                last:str = tokens[-1]
                if(last.startswith("__sfdc_trigger")):
                    #this is a trigger code execution
                    operation = TriggerOperation(logLine)
                elif(last.startswith(('Workflow:', 'Flow:'))):
                    pass
                elif(last.startswith("Validation:")):
                    pass
                elif(last.startswith("DuplicateDetector")):
                    pass
                else:
                    operation = MethodOperation(logLine)
                    pass
            elif(tokens[1] in ['FATAL_ERROR', 'EXCEPTION_THROWN']):
                operation = FatalErrorOp(logLine)
                if(self.findInStack(operation) is None):
                    lastOp = self.getOpenParentOperation(operation)
                    if(lastOp is not None):
                        operation.parent = lastOp if operation.get('parent', None) is None else operation.parent
                    #self.appendToStack(operation)
                return operation
                    # operation = MethodOperation(logLine)

        #The operation here is based on the log line, so it may already be in the stack
        if(operation is not None):
            if(operation.get('parent', None) == None and operation.isEntry()):
                operation.parent = self.getOpenParentOperation(operation)
            operation.tokens = tokens
            if(isinstance(operation,(MethodOperation,DMLOperation,ExecutionOperation,CalloutOperation,FlowOperation,TriggerOperation))):
                if(isinstance(operation, FlowOperation) and operation.eventType == 'FLOW_WRAPPER'):
                    operation = None
                    return None
                op = self.findInStack(operation)
                if(op is not None):
                    op.update(operation.__dict__)
                
                return operation
                # for topOfStack in Operation.OPSTACK:
                #     sti = Operation.OPSTACK.index(topOfStack)
                #     if(topOfStack.get('eventId') == operation.eventId):
                #         for key in od:
                #             topOfStack[key] = od.get(key)
                #         return operation
                #     try:
                #         if(isinstance(operation, FlowOperation) == False and topOfStack.get('name') == operation.name and topOfStack.get('eventType') == operation.eventType and topOfStack.get('eventSubType') == operation.eventSubType):
                #             #print(f"op.logLine: {opDict.get('lineNumber')} | operation.logLine: {operation.lineNumber} | op.eventId: {opDict.get('eventId')} | operation.eventId: {operation.eventId}")
                #             topOfStack.update(od)
                #             return operation
                #     except Exception as e:
                #         pp(operation.__dict__)
                #         pp(topOfStack)
                #         raise e
                #     if(topOfStack.get('finished') is not True):
                #         operation.parent = topOfStack

                # operation.appendTo(Operation.OPSTACK)
        return operation

    def getOpenParentOperation(self, opIn:Operation):
        if(len(self.OPERATIONS) == 0):
            return None
        for op in reversed(self.OPERATIONS):
            if(op.get('finished', False) == False and op.eventId != opIn.eventId):
                return op
        return None


    def findInStack(self, op:Operation) -> Operation:
        if(len(self.OPERATIONS) == 0):
            self.appendToStack(op)
            return op
        # loop through the stack backwards
        for stackOp in self.OPERATIONS[::-1]:
            if(stackOp.eventId == op.eventId):
                #stackOp.update(op.__dict__)
                return op
            elif(isinstance(op, FlowOperation) == False):
                try:
                    if(stackOp.name == op.name and stackOp.eventType == op.eventType and stackOp.eventSubType == op.eventSubType):
                        #stackOp.update(op.__dict__)
                        return op
                except Exception as e:
                    pp(op)
                    pp(stackOp)
                    raise e
        # wasn't found in the stack so add it 
        self.appendToStack(op)
        return None

    def appendToStack(self, op:Operation):
        self.OPERATIONS.append(op)

    @staticmethod
    def getLastOperation(operation)->dict:
        if(operation is not None):

            if(isinstance(operation, FlowOperation)):
                pass
            if(isinstance(operation, MethodOperation)):
                pass
            if(isinstance(operation, TriggerOperation)):
                pass
            if(isinstance(operation, CalloutOperation)):
                pass
            if(isinstance(operation, DMLOperation)):
                pass
            if(isinstance(operation, ExecutionOperation)):
                pass

        return None