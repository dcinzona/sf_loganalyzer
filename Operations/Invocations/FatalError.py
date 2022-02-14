from Operations.Operation import Operation

class FatalErrorOp(Operation):
    def __init__(self, ll):
        super(FatalErrorOp, self).__init__(ll)
        self.eventType = 'FATAL_ERROR'
        self.name = ll.lineSplit[-1]
        self.logLine = ll
        self.eventId = f'{self.eventType}|{self.name}'