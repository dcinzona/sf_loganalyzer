
from pprint import pp
import traceback
from Operations.EntryOrExit import EntryOrExit, EntryPoints, ExitPoints
from Operations.OpUtils import dynamicDict

class kLimit:
    value:int = 0
    maxValue:int = 0
    def __init__(self, val, maxVal):
        self.value = val
        self.maxValue = maxVal

class LimitData(dict):
    def __init__(self, initializer:dict = None):
        if(initializer is not None):
            super().__init__(initializer)
        else:
            self['startlimits'] = {}
            self['endlimits'] = {}
        
    def addLimit(self, start:bool, key:str, val:dict):
        if(start):
            self['startlimits'].setdefault(key, val)
            #self['startlimits'][key] = val
        else:
            self['endlimits'].setdefault(key, val)
            #self['endlimits'][key] = val


class Operation(dynamicDict):
    name:str = ''
    lines:list[str] = []
    lineNumber:int = 0
    timeStamp:str = None
    eventType:str = None
    eventId:str = None
    eventSubType:str = None
    operationAction:str = ''
    #tokensLength:int = 0
    operations:list = []
    LAST_OPERATION:dict = None
    finished:bool = False

    def __init__(self, *args, **kwargs):
        super(dynamicDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

    def __init__(self, ll):
        # This is a horrible hack
        if(str(ll.__class__) == "<class 'Operations.LogLine.LogLine'>"):            
            tokens = ll.lineSplit
            self.operationAction = tokens[1]
            self.lineNumber = ll.lineNumber
            linestr = ll.line
            self.lines.append(linestr)
            self.timeStamp = tokens[0] if self.timeStamp is None else self.timeStamp
            if(self.operationAction in [EntryPoints.CODE_UNIT_STARTED]):
                self.clusterNode = True
            elif(self.get('clusterNode', False) != True):
                self.clusterNode = False
            super(Operation, self).__init__(self.__dict__)
        if(isinstance(ll,dict)):
            super(Operation, self).__init__(ll)
       

    def isEntry(self):
        if(self.get('eventId','').startswith('ERROR|')):
            return True
        return self.operationAction in [EntryPoints.CODE_UNIT_STARTED, ExitPoints.FLOW_CREATE_INTERVIEW_END, EntryPoints.METHOD_ENTRY]
        
    def isExit(self):
        return self.operationAction in ExitPoints.EXIT_POINTS

    def appendTo(self, opStack:list):
        opStack.append(self)

    @staticmethod
    def print(cls, msg=None):
        return
        #print(json.dumps(self, default=lambda x: x.__dict__, indent=4, sort_keys=True))
        try:
            ln = f'[{cls.lineNumber}] {cls.eventType}|{cls.name}' if msg is None else f'[{cls.lineNumber}] {msg}'
            print(ln)
        except Exception as e:
            pp(traceback.format_exc())
            print(cls.lineNumber)
            print(cls.__class__)
            exit(e)

    @staticmethod
    def getType(tokens:list[str]=None):
        if(tokens is None):
            return None
        evnt:str = tokens[1]
        last:str = tokens[-1].split('.')[0]
        if(evnt.startswith('METHOD_')):
            return 'apex'
        elif(evnt.startswith('FLOW_')):
            return 'flows'
        elif(evnt.startswith('SOQL_')):
            return 'soql'
        elif(evnt.startswith('CALLOUT_')):
            return 'callout'
        elif(evnt.startswith('DML_')):
            return 'dml'
        elif(evnt.startswith('CODE_UNIT_')):
            if(last.startswith("__sfdc_trigger")):
                return 'triggers'
            elif(last.startswith('Workflow:')):
                return 'workflows'
            elif(last.startswith('Flow:')):
                return 'flows'
            elif(last.startswith("Validation:")):
                return 'validations'
            elif(last.startswith("DuplicateDetector")):
                return 'duplicateDetector'
            elif(last.lower() not in ['system','database','userInfo']):
                return 'apex'
        elif(evnt in ['FATAL_ERROR', 'EXCEPTION_THROWN']):
            return 'exceptions'
        return 'Unknown'

    # @staticmethod
    # def findSelfinStack(op, stack:list[dict], eventIdOnly=False) -> dict:
    #     if(len(stack) > 0):
    #         for i in range(len(stack)-1, -1, -1):
    #             sop = stack[i]
    #             if(sop.get('eventId') == op.eventId):
    #                 return stack.pop(i)
    #             if(eventIdOnly == False):
    #                 try:
    #                     if(sop.get('name') == op.name and sop.get('eventType') == op.eventType, sop.get('eventSubType') == op.eventSubType):
    #                         return stack.pop(i)
    #                     # if(sop.eventType == op.eventType and sop.eventSubType == op.eventSubType):
    #                     #     return sop,i
    #                 except Exception:
    #                     print(traceback.format_exc())
    #                     print(op)
    #                     pp(stack[i])
    #                     exit()
    #     print(f'{op.name} not found in stack :(')
    #     pp(stack)
    #     pp(op)
    #     return None

