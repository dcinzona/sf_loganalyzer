from ..Operation import Operation


class DMLOperation(Operation):
    LAST_OPERATION: dict = None

    def __init__(self, ll):
        super(DMLOperation, self).__init__(ll)
        self.logLine = ll
