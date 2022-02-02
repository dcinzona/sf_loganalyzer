from Operations.Operation import Operation

class ExecutionOperation(Operation):

    def __init__(self, tokens:list[str], lineNumber:int):
        super().__init__(tokens, lineNumber)
        self.eventType = 'Execution'
