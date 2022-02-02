from Operations.Operation import Operation

class MethodOperation(Operation):

    def __init__(self, ll):
        super().__init__(ll.lineSplit, ll.lineNumber)

        self.eventType = 'APEX'
        self.eventId = self.tokens[-1]
        self.eventSubType = 'METHOD'