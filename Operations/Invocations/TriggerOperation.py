from pprint import pp
from Operations.Operation import Operation

class TriggerOperation(Operation):

    TRIGGERSTACK:list[dict] = []
    LAST_OPERATION:dict = None
        
    def __init__(self, ll):
        super(TriggerOperation, self).__init__(ll)
        tokens = ll.lineSplit
        self.eventType = 'TRIGGER'
        self.eventId = tokens[-2]
        self.lineNumber = ll.lineNumber
        self.name = self.eventId # tokens[-1].split('/')[1]
        TriggerOperation.LAST_OPERATION = None
        if(tokens[1] == 'CODE_UNIT_STARTED'):
            TriggerOperation.TRIGGERSTACK.append(self.__dict__.copy())
        else:
            d = TriggerOperation.TRIGGERSTACK[-1] if len(TriggerOperation.TRIGGERSTACK) > 0 else self
            for key in d:
                self.__setattr__(key, d.get(key))
        
        if(tokens[1] == 'CODE_UNIT_FINISHED'):
            t = TriggerOperation.TRIGGERSTACK.pop()
            self.update(t)
        
