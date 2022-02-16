import json
from pprint import pp
from Operations.LogLine import LogLine
from Operations.OpUtils import dynamicDict
from Operations.Operation import LimitData, Operation

    
    
class FlowOperation(Operation):

    FLOWSTACK:list = []
    LAST_OPERATION:dict = None
    FLOW_WITH_LIMITS = None
    CREATE_INTERVIEW_TYPE:str = None
    CURRENT_FLOW = None

    # have to check the previous line to determine if this is a flow or a process builder
    # seems like process builders all have the last element in the previous line starting with 301r
    # flows don't have that last element, so they start with 300r
    def __init__(self, ll:LogLine):        
        super(FlowOperation, self).__init__(ll)
        tokens = ll.lineSplit        
        self.line = ll.line
        self.lineSplit = ll.lineSplit
        if(len(tokens[-1]) == 0):
            tokens.pop()
            self.eventType = 'FLOW'
        #tokens.pop() if tokens[-1] == '' else None
        if(tokens[1] == 'CODE_UNIT_STARTED'):
            self.codeUnitStarted(tokens)
        elif(tokens[1] == "FLOW_CREATE_INTERVIEW_BEGIN"):
            self.flowCreateInterviewBegin(tokens)
        elif(tokens[1] == "FLOW_CREATE_INTERVIEW_END"):
            self.flowCreateInterviewEnd(tokens, ll.lineNumber)

        elif(tokens[1] in ["FLOW_START_INTERVIEW_BEGIN",'FLOW_INTERVIEW_FINISHED']):
            d = self.getFlowFromStack(tokens[2])
            if(d is not None):
                self.update(d)
                # for key in d.__dict__:
                #     self.__setattr__(key, d.get(key))
                if(tokens[1] == 'FLOW_INTERVIEW_FINISHED'):
                    self.finished = True
                    #FlowOperation.LAST_OPERATION = FlowOperation.FLOWSTACK[i]#.pop(i)
            else:
                pp(FlowOperation.FLOWSTACK)
                raise Exception(f'{tokens[2]} not found in stack')
            #FlowOperation.FLOW_WITH_LIMITS = self
            #FlowOperation.LAST_OPERATION = FlowOperation.FLOW_WITH_LIMITS
        
        elif(tokens[1].endswith("_LIMIT_USAGE")):
            self.update(FlowOperation.FLOWSTACK[-1])
            self.setFlowLimitUsage(tokens)
            return
            # 15:09:38.311 (6311977364)|FLOW_START_INTERVIEW_LIMIT_USAGE|Flow Unique ID|Flow Name
            if(FlowOperation.FLOW_WITH_LIMITS is not None):
                for key in FlowOperation.FLOW_WITH_LIMITS:
                    self.__setattr__(key, FlowOperation.FLOW_WITH_LIMITS.get(key))
                self.setFlowLimitUsage(tokens)
                FlowOperation.LAST_OPERATION = FlowOperation.FLOW_WITH_LIMITS


    def appendToStack(self):
        FlowOperation.FLOWSTACK.append(self)
        #self.appendTo(FlowOperation.FLOWSTACK)
        #FlowOperation.FLOWSTACK.append(self.__dict__.copy())

    def getFlowFromStack(self,eventId:str):
        for f in FlowOperation.FLOWSTACK[::-1]:
            if(f.eventId == eventId):
                #print(f'1: {f.eventId} == {eventId}')
                return f #, FlowOperation.FLOWSTACK.index(f)
            else:
                #print(f'0: {f.eventId} != {eventId}')
                #f.print(self)
                pass
        pp(FlowOperation.FLOWSTACK)
        raise Exception(f'{eventId} not found in stack')

    def codeUnitStarted(self, tokens:list=None):
        self.name = tokens[-1]
        self.eventType = 'FLOW_WRAPPER'
        #FlowOperation.FLOWSTACK.append(self)
    
    
    def flowCreateInterviewBegin(self, tokens:list=None):
        FlowOperation.LAST_OPERATION = None
        """
        Description: Used to identify whether flow is a process builder or a flow
        """
        # Visual Flow
        # 15:09:38.105 (6113840972)|FLOW_CREATE_INTERVIEW_BEGIN|00Dr00000002V3c|300r00000001oD9|
        # Process Builder
        # 15:09:38.310 (6310353162)|FLOW_CREATE_INTERVIEW_BEGIN|00Dr00000002V3c|300r00000001oDh|301r0000000kzyr
        FlowOperation.FLOW_WITH_LIMITS = None
        FlowOperation.CREATE_INTERVIEW_TYPE = self.getFlowType(tokens)
        self.eventType = 'FLOW_WRAPPER'
        self.appendToStack()
    
    def flowCreateInterviewEnd(self, tokens:list=None, lineNumber:int=None):
        """
        Description: Sets the unique ID of the flow interview
        """
        # 15:09:38.105 (6113904308)|FLOW_CREATE_INTERVIEW_END|Flow Unique ID|Flow Name
        if(len(FlowOperation.FLOWSTACK) > 0):
            f = FlowOperation.FLOWSTACK[-1] #dynamicDict(FlowOperation.FLOWSTACK[-1])
            if(f.eventType == 'FLOW_WRAPPER'):
                FlowOperation.CURRENT_FLOW = FlowOperation.FLOWSTACK.pop()
            else:
                FlowOperation.CURRENT_FLOW = f#f.__dict__.copy()
        else:
            raise Exception("No flows in the stack.  This is a bug")
        
        #self.update(FlowOperation.CURRENT_FLOW)
        self.eventId = tokens[2]
        self.name = tokens[-1]
        self.eventType = FlowOperation.CREATE_INTERVIEW_TYPE
        self.eventSubType = 'FLOW_CREATE_INTERVIEW_END'
        self.lineNumber = lineNumber # if self.lineNumber is None else self.lineNumber
        self.appendToStack()
    
        
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
            if('limits' not in self.FLOW_WITH_LIMITS):
                self.limits = LimitData()
                self.FLOW_WITH_LIMITS['limits'] = self.limits
            else:
                limits = self.FLOW_WITH_LIMITS['limits']
                self.limits = LimitData(limits)
                for k in limits:
                    self.limits[k] = limits[k]
            limitToken = tokens[-1]
            operationAction = tokens[1]
            limitArray = limitToken.split(":")
            limitName = limitArray[0].strip()
            limitValue = limitArray[1].strip().split('out of')[0].strip()
            limitMax = limitArray[1].strip().split('out of')[1].strip()
            self.limits.addLimit(start=operationAction.startswith('FLOW_START_INTERVIEW_'), key=limitName, val={'_used':limitValue, 'out_of':limitMax})
            self.FLOW_WITH_LIMITS['limits'] = self.limits
