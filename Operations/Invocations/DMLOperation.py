from Operations.Invocations.FatalError import FatalErrorOp
from Operations.Operation import Operation


class DMLOperation(Operation):
    LAST_OPERATION: dict = None

    def __init__(self, ll):
        super(FatalErrorOp, self).__init__(ll)
        self.logLine = ll
