from Operations.Operation import Operation

class FatalErrorOp(Operation):
    #PREV=None
    def __init__(self, ll):
        super(FatalErrorOp, self).__init__(ll)
        self.eventType = 'FATAL_ERROR'
        self.name = ll.lineSplit[-1]
        self.logLine = ll
        self.eventId = f'{self.eventType}|{self.name}'
        self.finished = False
        self.eventSubType = self.name.split(':')[0]
        # if(FatalErrorOp.PREV is not None and self.eventId == FatalErrorOp.PREV.eventId):
        #     self = FatalErrorOp.PREV
        # else:
        #     FatalErrorOp.PREV = self