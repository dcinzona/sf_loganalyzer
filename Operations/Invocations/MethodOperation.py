from pprint import pp
from Operations.Operation import Operation

class MethodOperation(Operation):
    METHODSTACK:list[Operation] = []
    def __init__(self, ll):
        super().__init__(ll.lineSplit, ll.lineNumber)
        tokens = ll.lineSplit
        self.eventType = 'APEX'
        self.eventId = tokens[-1]
        self.eventSubType = 'METHOD'

        if(tokens[1].startswith('METHOD_ENTRY')):
            # 15:09:44.547 (12548827536)|METHOD_ENTRY|[17]|01pr000000120Tt|SF86RecordSyncHelper.syncMilitaryToSect15(List<Military_Service__c>)
            self.name = tokens[-1]
            Operation.OPSTACK.append(self)
            MethodOperation.METHODSTACK.append(self)
        else:
            op = Operation.OPSTACK[-1] if len(Operation.OPSTACK) > 0 else None
            if(op and op.eventSubType == 'METHOD'):
                pass
                #op.addChild(self)
                #Operation.OPSTACK.append(self)
            mop = MethodOperation.METHODSTACK[-1] if len(MethodOperation.METHODSTACK) > 0 else None
            if(mop and mop.eventSubType == 'METHOD'):
                #self=mop
                pass
        
        if(tokens[1].startswith('METHOD_EXIT')):
            # 15:09:44.547 (12548827536)|METHOD_EXIT|[17]|01pr000000120Tt|SF86RecordSyncHelper.syncMilitaryToSect15(List<Military_Service__c>)
            self.name = tokens[-1]
            Operation.OPSTACK.pop() if len(Operation.OPSTACK) > 0 else None
            prev = MethodOperation.METHODSTACK.pop() if len(MethodOperation.METHODSTACK) > 0 else None
            if(prev is None):
                #pp(self.name)
                self.print()
            else:
                self.print() if self.name != prev.name else None
