from Operations.Operation import Operation


class FatalErrorOp(Operation):
    # PREV=None
    def __init__(self, ll):
        super(FatalErrorOp, self).__init__(ll)
        self.eventType = ll.lineSplit[1]  # 'FATAL_ERROR'
        self._name = ll.lineSplit[-1]
        self.logLine = ll
        self.eventId = f'ERROR|{self.name}'
        self.finished = True
        self.eventSubType = self.name.split(':')[0]

    @property
    def safeName(self):
        if(self.name.startswith('System.LimitException:')):
            return self.name
        return self.name.split(':')[0]

    @property
    def name(self):
        return self._name
