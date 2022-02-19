from pprint import pp
from Operations.EntryOrExit import ExitPoints, EntryPoints
from Operations.Operation import Operation

class TriggerOperation(Operation):

    TRIGGERSTACK:list[dict] = []
        
    def __init__(self, ll):
        super(TriggerOperation, self).__init__(ll)
        tokens = ll.lineSplit
        self.eventType = 'TRIGGER'
        self.eventId = tokens[-2]
        self.lineNumber = ll.lineNumber
        self.name = self.eventId # tokens[-1].split('/')[1]
        if(tokens[1] == 'CODE_UNIT_STARTED'):
            TriggerOperation.TRIGGERSTACK.append(self)        
        elif(tokens[1] == 'CODE_UNIT_FINISHED'):
            t = self.findInStack() # TriggerOperation.TRIGGERSTACK.pop()
            if(t is None):
                raise Exception('Could not find matching TriggerOperation in TriggerOperation.TRIGGERSTACK')
            self.update(t)
            self.finished = True

    def findInStack(self):
        if(len(TriggerOperation.TRIGGERSTACK) == 0):
            raise Exception('TriggerOperation.TRIGGERSTACK is empty')
        if(len(TriggerOperation.TRIGGERSTACK) == 1 and self.operationAction == 'CODE_UNIT_FINISHED'):
            return TriggerOperation.TRIGGERSTACK.pop() 
        else:
            for x in reversed(TriggerOperation.TRIGGERSTACK):
                if(self.isMatch(x)):
                    return TriggerOperation.TRIGGERSTACK.pop(TriggerOperation.TRIGGERSTACK.index(x))
        return None

    def isMatch(self, stackOp:Operation):
        if(self.operationAction == ExitPoints.CODE_UNIT_FINISHED and stackOp.operationAction == EntryPoints.CODE_UNIT_STARTED):
            return self.name == stackOp.name
        return False
        
