from Operations.Operation import Operation

class DMLOperation(Operation):
    def __init__(self, ll):
        super().__init__(ll.lineSplit, ll.lineNumber)
        self.logLine = ll