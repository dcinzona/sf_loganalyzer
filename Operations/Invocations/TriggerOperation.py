from pprint import pp
from Operations.Operation import Operation

class TriggerOperation(Operation):

    TRIGGERSTACK:list[Operation] = []

    def __init__(self, ll):
        super().__init__(ll.lineSplit, ll.lineNumber)
        tokens = ll.lineSplit
        self.eventType = 'TRIGGER'
        self.eventId = tokens[-2]
        tokens = ll.lineSplit
        self.eventSubType = 'TRIGGER'


        if(tokens[1].startswith(('CODE_UNIT_STARTED'))):
            # 15:09:44.547 (12548827536)|METHOD_ENTRY|[17]|01pr000000120Tt|SF86RecordSyncHelper.syncMilitaryToSect15(List<Military_Service__c>)
            self.name = tokens[-1]
            Operation.OPSTACK.append(self)
            TriggerOperation.TRIGGERSTACK.append(self)
        else:
            mop = TriggerOperation.TRIGGERSTACK[-1] if len(TriggerOperation.TRIGGERSTACK) > 0 else None
            self = mop if mop else self
        
        if(tokens[1].startswith(('CODE_UNIT_FINISHED'))):
            # 15:09:44.547 (12548827536)|METHOD_EXIT|[17]|01pr000000120Tt|SF86RecordSyncHelper.syncMilitaryToSect15(List<Military_Service__c>)
            #self.name = tokens[-1]
            #Operation.OPSTACK.pop() if len(Operation.OPSTACK) > 0 else None
            prev = TriggerOperation.TRIGGERSTACK.pop() if len(TriggerOperation.TRIGGERSTACK) > 0 else None
            if(prev is None):
                self.print()
            else:
                prev.print() #self.print() #if self.name != prev.name else None