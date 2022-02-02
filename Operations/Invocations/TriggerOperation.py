from Operations.Operation import Operation

class TriggerOperation(Operation):

    def __init__(self, ll):
        super().__init__(ll.lineSplit, ll.lineNumber)
        tokens = ll.lineSplit
        self.name = tokens[-1]
        self.line = '|'.join(tokens)
        self.lineSplit = tokens
        self.timeStamp = self.lineSplit[0]
        self.eventType = 'APEX'
        self.eventId = tokens[-2]
        self.eventSubType = 'TRIGGER'