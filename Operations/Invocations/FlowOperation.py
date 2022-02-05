import json
from pprint import pp
from Operations.LogLine import LogLine
from Operations.Operation import Operation

    
    
class FlowOperation(Operation):

    LOCAL_STACK:list = []
    FLOW_WITH_LIMITS = None
    CREATE_INTERVIEW_TYPE:str = None

    # have to check the previous line to determine if this is a flow or a process builder
    # seems like process builders all have the last element in the previous line starting with 301r
    # flows don't have that last element, so they start with 300r
    def __init__(self, ll:LogLine):
        super().__init__(ll)
        tokens = ll.lineSplit
        if(len(tokens[-1]) == 0):
            tokens.pop()
            self.eventType = 'FLOW'
        #tokens.pop() if tokens[-1] == '' else None
        if(tokens[1] == 'CODE_UNIT_STARTED'):
            self.name = tokens[-1]
            self.eventType = 'FLOW_WRAPPER'
            #FlowOperation.LOCAL_STACK.append(self)
            return
        if(tokens[1] == "FLOW_CREATE_INTERVIEW_BEGIN"):
            # Visual Flow
            # 15:09:38.105 (6113840972)|FLOW_CREATE_INTERVIEW_BEGIN|00Dr00000002V3c|300r00000001oD9|
            # Process Builder
            # 15:09:38.310 (6310353162)|FLOW_CREATE_INTERVIEW_BEGIN|00Dr00000002V3c|300r00000001oDh|301r0000000kzyr
            FlowOperation.FLOW_WITH_LIMITS = None
            FlowOperation.CREATE_INTERVIEW_TYPE = self.getFlowType(tokens)
            self.eventType = 'FLOW_WRAPPER'
            
        if(self.operationAction == "FLOW_CREATE_INTERVIEW_END"):
            # 15:09:38.105 (6113904308)|FLOW_CREATE_INTERVIEW_END|Flow Unique ID|Flow Name
            self.eventId = tokens[2]
            self.name = tokens[-1]
            self.eventType = FlowOperation.CREATE_INTERVIEW_TYPE
            self.appendToStack(self.__dict__)

        if(tokens[1] in ["FLOW_START_INTERVIEW_BEGIN",'FLOW_INTERVIEW_FINISHED']):
            d,i = FlowOperation.getFlowFromStack(tokens[2])
            if(d is not None):
                for key in d:
                    self.__setattr__(key, d.get(key))
                if(tokens[1] == 'FLOW_INTERVIEW_FINISHED'):
                    FlowOperation.LOCAL_STACK.pop(i)
            else:
                pp(FlowOperation.LOCAL_STACK)
                raise Exception(f'{tokens[2]} not found in stack')
            FlowOperation.FLOW_WITH_LIMITS = self.__dict__
            
        if(tokens[1].endswith("_LIMIT_USAGE")):
            # 15:09:38.311 (6311977364)|FLOW_START_INTERVIEW_LIMIT_USAGE|Flow Unique ID|Flow Name
            if(FlowOperation.FLOW_WITH_LIMITS is not None):
                for key in FlowOperation.FLOW_WITH_LIMITS:
                    self.__setattr__(key, FlowOperation.FLOW_WITH_LIMITS.get(key))
                self.setFlowLimitUsage(tokens)


    @classmethod
    def appendToStack(cls, d:dict):
        cls.LOCAL_STACK.append(d)

    @classmethod
    def getFlowFromStack(cls,eventId:str):
        if(len(cls.LOCAL_STACK) == 0):
            return None, None
        for i in range(len(cls.LOCAL_STACK)):
            d = cls.LOCAL_STACK[i]
            if(d.get('eventId') == eventId):
                return d, i
        return None, None

        
    
    def print(self):
        Operation.print(self)

    
    def getFlowType(self, tokens:list=None):
        if(len(tokens)) == 4:
            return "FLOW"

        return 'PROCESS BUILDER'

    def setFlowLimitUsage(self, tokens):
        # 15:09:38.311 (6312006106)|FLOW_START_INTERVIEW_LIMIT_USAGE|SOQL queries: 12 out of 100
        # 15:09:38.311 (6312017543)|FLOW_START_INTERVIEW_LIMIT_USAGE|SOQL query rows: 103 out of 50000
        # 15:09:38.311 (6312026507)|FLOW_START_INTERVIEW_LIMIT_USAGE|SOSL queries: 0 out of 20
        # 15:09:38.311 (6312034896)|FLOW_START_INTERVIEW_LIMIT_USAGE|DML statements: 6 out of 150
        # 15:09:38.311 (6312042980)|FLOW_START_INTERVIEW_LIMIT_USAGE|DML rows: 6 out of 10000
        # 15:09:38.311 (6312093354)|FLOW_START_INTERVIEW_LIMIT_USAGE|CPU time in ms: 1310 out of 15000
        # 15:09:38.311 (6312173151)|FLOW_START_INTERVIEW_LIMIT_USAGE|Heap size in bytes: 3431 out of 6000000
        # 15:09:38.311 (6312184175)|FLOW_START_INTERVIEW_LIMIT_USAGE|Callouts: 0 out of 100
        # 15:09:38.311 (6312192644)|FLOW_START_INTERVIEW_LIMIT_USAGE|Email invocations: 0 out of 10
        # 15:09:38.311 (6312200540)|FLOW_START_INTERVIEW_LIMIT_USAGE|Future calls: 0 out of 50
        # 15:09:38.311 (6312207873)|FLOW_START_INTERVIEW_LIMIT_USAGE|Jobs in queue: 0 out of 50
        # 15:09:38.311 (6312215669)|FLOW_START_INTERVIEW_LIMIT_USAGE|Push notifications: 0 out of 10
        if(len(tokens)) == 3:
            limitToken = tokens[-1]
            operationAction = tokens[1]
            limitArray = limitToken.split(":")
            limitName = limitArray[0].strip()
            limitValue = limitArray[1].strip().split('out of')[0].strip()
            limitMax = limitArray[1].strip().split('out of')[1].strip()
            self.limits.addLimit(start=operationAction.startswith('FLOW_START_INTERVIEW_'), key=limitName, val={'_used':limitValue, 'out_of':limitMax})