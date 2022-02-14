from pprint import pp
from Operations.EntryOrExit import EntryOrExit
from Operations.Operation import Operation
from Operations.Invocations.CalloutOperation import CalloutOperation
from Operations.Invocations.DMLOperation import DMLOperation
from Operations.Invocations.ExecutionOperation import ExecutionOperation
from Operations.Invocations.FlowOperation import FlowOperation
from Operations.Invocations.MethodOperation import MethodOperation
from Operations.Invocations.TriggerOperation import TriggerOperation

class OperationFactory():

    @staticmethod
    def createOperation(logLine):
        tokens:list[str]  = logLine.line.split("|");
        operation = None
        if(tokens and len(tokens)>1):
            if(tokens[1].startswith("METHOD_")):
                operation = MethodOperation(logLine)
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
                    #this is a flow code execution
                    #operation = FlowOperation(logLine)
                    pass
                elif(last.startswith("Validation:")):
                    pass
                else:
                    pass
            elif(tokens[1] == 'FATAL_ERROR'):
                #should probably end here
                pass
                    # operation = MethodOperation(logLine)

        #The operation here is based on the log line, so it may already be in the stack
        if(operation is not None):
            od = operation.__dict__.copy()
            od['tokens'] = tokens
            if(isinstance(operation,(MethodOperation,DMLOperation,ExecutionOperation,CalloutOperation,FlowOperation,TriggerOperation))):
                if(isinstance(operation, FlowOperation) and operation.eventType == 'FLOW_WRAPPER'):
                    return None
                if(len(Operation.OPSTACK) == 0):
                    Operation.OPSTACK.append(od)
                    return operation
                for opDict in Operation.OPSTACK:
                    if(opDict.get('eventId') == operation.eventId):
                        for key in operation.__dict__:
                            opDict[key] = operation.__dict__.get(key)
                        return operation
                    try:
                        if(isinstance(operation, FlowOperation) == False and opDict.get('name') == operation.name and opDict.get('eventType') == operation.eventType and opDict.get('eventSubType') == operation.eventSubType):
                            #print(f"op.logLine: {opDict.get('lineNumber')} | operation.logLine: {operation.lineNumber} | op.eventId: {opDict.get('eventId')} | operation.eventId: {operation.eventId}")
                            opDict.update(od)
                            return operation
                    except Exception as e:
                        pp(operation.__dict__)
                        pp(opDict)
                        raise e

                operation.appendTo(Operation.OPSTACK)
        
        return operation

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