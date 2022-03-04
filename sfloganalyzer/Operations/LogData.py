from .OperationStack import OperationStack


class LogData:
    logReversed = []
    lineNumber = 0
    _stack: OperationStack = None
    _instance = None

    def getStack(self) -> OperationStack:
        if self._stack is None:
            self._stack = OperationStack()
        return self._stack

    def __new__(cls) -> None:
        if cls._instance is None:
            cls._instance = super(LogData, cls).__new__(cls)
            cls._instance._stack = OperationStack()
            # Put any initialization here.
        return cls._instance
