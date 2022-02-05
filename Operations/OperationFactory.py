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
                    # operation = MethodOperation(logLine)


        if(operation is not None):
            if(isinstance(operation,(MethodOperation,DMLOperation,ExecutionOperation,CalloutOperation,FlowOperation,TriggerOperation))):
                if(isinstance(operation, FlowOperation) and operation.eventType == 'FLOW_WRAPPER'):
                    return None
                if(len(Operation.OPSTACK) == 0):
                    Operation.OPSTACK.append(operation.__dict__)
                    return operation
                for op in Operation.OPSTACK:
                    if(op.get('eventId') == operation.eventId):
                        for key in operation.__dict__:
                            op[key] = operation.__dict__.get(key)
                        return operation
                    try:
                        if(isinstance(operation, FlowOperation) == False and op.get('name') == operation.name and op.get('eventType') == operation.eventType and op.get('eventSubType') == operation.eventSubType):
                            for key in operation.__dict__:
                                op[key] = operation.__dict__.get(key)
                            return operation
                    except Exception as e:
                        pp(operation.__dict__)
                        pp(op)
                        raise e

                Operation.OPSTACK.append(operation.__dict__)
        
        return operation