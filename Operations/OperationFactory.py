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
    def createOperation(logLine) -> Operation:
        tokens:list[str]  = logLine.line.split("|");
        operation:Operation = None
        if(tokens and len(tokens)>1):
            if(tokens[1].startswith("METHOD_")):
                operation = MethodOperation(logLine)
            elif(tokens[1].startswith("DML_")):
                operation = DMLOperation(logLine);
            elif(tokens[1].startswith("EXECUTION_")):
                pass
                #return ExecutionOperation(tokens, logLine.lineNumber);
            elif(tokens[1].startswith("CALLOUT")):
                operation = CalloutOperation(logLine);
            elif(tokens[1].startswith("FLOW_")):
                if(tokens[1] in EntryOrExit.ALL):
                    operation = FlowOperation(logLine);
            elif(tokens[1].startswith("CODE_UNIT_")):
                #Check if this is a trigger
                last:str = tokens[-1]
                if(last.find("trigger")>-1):
                    #this is a trigger code execution
                    operation = TriggerOperation(logLine)
                elif(last.startswith(('Workflow:', 'Flow:'))):
                    #this is a flow code execution
                    operation = FlowOperation(logLine)
                else:
                    operation = MethodOperation(logLine)
                
        return operation