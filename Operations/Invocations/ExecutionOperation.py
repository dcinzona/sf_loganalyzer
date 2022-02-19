from Operations.LogLine import LogLine
from Operations.Operation import Operation

class ExecutionOperation(Operation):
    LAST_OPERATION:dict = None

    def __init__(self, ll:LogLine):
        super(ExecutionOperation, self).__init__(ll)
        self.eventType = 'EXECUTION'
