from pprint import pp
from Operations.Operation import Operation
import re

from Operations.OperationStack import OperationStack
constructorPattern = re.compile(r'(\w+)\.\1\(\)$')

class MethodOperation(Operation):

    METHODSTACK:list = []
    LAST_OPERATION:dict = None

    def __init__(self, ll):
        tokens = ll.lineSplit
        self.eventType = 'APEX'
        self.eventId = f'{tokens[-3]}|{tokens[-2]}|{tokens[-1]}' #[id]MethodName
        self.eventSubType = 'METHOD'
        self.isContructor(tokens)
        MethodOperation.LAST_OPERATION = None
        if(tokens[1] in ['METHOD_ENTRY','CODE_UNIT_STARTED']):
            # 15:09:44.547 (12548827536)|METHOD_ENTRY|[17]|01pr000000120Tt|SF86RecordSyncHelper.syncMilitaryToSect15(List<Military_Service__c>)
            self.name = tokens[-1]
            self.lineNumber = ll.lineNumber
            MethodOperation.METHODSTACK.append(self.__dict__.copy())
        
        if(tokens[1] in ['METHOD_EXIT','CODE_UNIT_FINISHED']):
            d = None
            # 15:09:44.547 (12548827536)|METHOD_EXIT|[17]|01pr000000120Tt|SF86RecordSyncHelper.syncMilitaryToSect15(List<Military_Service__c>)
            if(len(MethodOperation.METHODSTACK) == 1 and tokens[1] == 'METHOD_EXIT'):
                d = MethodOperation.METHODSTACK.pop() 
            elif(len(MethodOperation.METHODSTACK) > 1):
                d = self.findSelfinStack(True)
            else:
                raise Exception('MethodOperation.METHODSTACK is empty')
            
            if(d is not None):
                MethodOperation.LAST_OPERATION = d
                for key in d:
                    if(key != 'lineNumber'):
                        object.__setattr__(self, key, d.get(key))
            else:
                pp(MethodOperation.METHODSTACK)
                print('^ METHODSTACK ^')
                pp(self.__dict__)
                raise Exception('Could not find matching MethodOperation in MethodOperation.METHODSTACK')
        
        #super(MethodOperation, self).__init__(ll) 
    
    def findSelfinStack(self, pop:bool):
        for idx,x in enumerate(MethodOperation.METHODSTACK):
            if(x.get('eventId') == self.eventId):
                if(pop):
                    return MethodOperation.METHODSTACK.pop(idx)
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
        
        