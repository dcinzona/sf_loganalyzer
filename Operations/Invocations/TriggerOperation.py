from pprint import pp
from Operations.Operation import Operation

class TriggerOperation(Operation):

    LOCAL_STACK:list[dict] = []

        
    def __init__(self, ll):
        tokens = ll.lineSplit
        self._tokens = tokens
        self.eventType = 'TRIGGER'
        self.eventId = tokens[-2]
        self.name = tokens[-1].split('/')[1]
        super(TriggerOperation, self).__init__(ll)

        if(tokens[1] == 'CODE_UNIT_STARTED'):
            TriggerOperation.LOCAL_STACK.append(self.__dict__)
        else:
            d = TriggerOperation.LOCAL_STACK[-1] if len(TriggerOperation.LOCAL_STACK) > 0 else self
            for key in d:
                self.__setattr__(key, d.get(key))
        
        if(tokens[1] == 'CODE_UNIT_FINISHED'):
            d = TriggerOperation.LOCAL_STACK.pop()
            for key in d:
                self.__setattr__(key, d.get(key))
        
