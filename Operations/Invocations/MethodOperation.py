from pprint import pp
from Operations.Operation import Operation
import re

from Operations.OperationStack import OperationStack
constructorPattern = re.compile(r'(\w+)\.\1\(\)$')

class MethodOperation(Operation):

    LOCAL_STACK:list = []

    _eventId:str = None

    # @property
    # def constructor(self):
    #     if(self.name is not None):
    #         yield constructorPattern.match(self.name) is not None if self.name.find('.') != -1 else True
    #     yield False

    # @property 
    # def eventId(self):
    #     if(self.constructor):
    #         return f'CONSTRUCTOR:{self.name.split(".")[0]}'
    #     return self._eventId

    # @property
    # def name(self):
    #     return self._tokens[-1]

    def __init__(self, ll):
        tokens = ll.lineSplit
        self._tokens = tokens
        self.eventType = 'APEX'
        self.eventId = f'{tokens[-2]}{tokens[-1]}' #[id]MethodName
        self.eventSubType = 'METHOD'
        self.lineNumber = ll.lineNumber
        self.isContructor(tokens)
        if(tokens[1] in ['METHOD_ENTRY','CODE_UNIT_STARTED']):
            # 15:09:44.547 (12548827536)|METHOD_ENTRY|[17]|01pr000000120Tt|SF86RecordSyncHelper.syncMilitaryToSect15(List<Military_Service__c>)
            self.name = tokens[-1]
            MethodOperation.LOCAL_STACK.append(self.__dict__)
        
        if(tokens[1] in ['METHOD_EXIT','CODE_UNIT_FINISHED']):
            d = None
            # 15:09:44.547 (12548827536)|METHOD_EXIT|[17]|01pr000000120Tt|SF86RecordSyncHelper.syncMilitaryToSect15(List<Military_Service__c>)
            if(len(MethodOperation.LOCAL_STACK) == 1 and tokens[1] == 'METHOD_EXIT'):
                d = MethodOperation.LOCAL_STACK.pop()
            
            # elif(tokens[1] == 'METHOD_EXIT' and tokens[-1].find('.') == -1):
            #     self.name = f'{tokens[-1]}.{tokens[-1]}()'
            #     self.eventSubType = 'METHOD'
            #     mop,idxm = Operation.findSelfinStack(self, MethodOperation.LOCAL_STACK, False)
            #     if(mop is not None):
            #         self = MethodOperation.LOCAL_STACK.pop(idxm)
            #     else:
            #         print('!!!!not found in stack')
            #         print(self.__dict__)
            #         pp([x.__dict__ for x in MethodOperation.LOCAL_STACK])
            #         exit()
            elif(len(MethodOperation.LOCAL_STACK) > 1):
                d = self.findSelfinStack(True)
            else:
                raise Exception('MethodOperation.LOCAL_STACK is empty')
            
            if(d is not None):
                for key in d:
                    if(key != 'lineNumber'):
                        self.__setattr__(key, d.get(key))
            else:
                pp(self.__dict__)
                raise Exception('Could not find matching MethodOperation in MethodOperation.LOCAL_STACK')
        
        #super(MethodOperation, self).__init__(ll) 
    
    def findSelfinStack(self, pop:bool):
        for idx,x in enumerate(MethodOperation.LOCAL_STACK):
            if(x.get('eventId') == self.eventId):
                if(pop):
                    return MethodOperation.LOCAL_STACK.pop(idx)
                else:
                    return x
        return None

    def isContructor(self, tokens:list):
        name = tokens[-1].strip()
            
        result = constructorPattern.match(name) is not None if name.find('.') != -1 else True
        # if(name.find('LeadDA.LeadDA()') > -1):
        #     print(result)
        #     print(constructorPattern.match(name))
        #     print(name)
        #     exit()
        if(result):
            self.name = name.split('.')[0]
            self.eventSubType = 'CONSTRUCTOR'
            self.eventId = f'CONSTRUCTOR:{self.name}'
        self.constructor = result
        
        