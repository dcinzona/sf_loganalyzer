
import json

from Operations.EntryOrExit import EntryPoints


class Operation:
    name:str
    lines:list[str] = []
    lineNumber:int = 0
    tokens:list[str] = []
    timeStamp:str = None
    eventType:str = None
    eventId:str = None
    eventSubType:str = None
    operationAction:str = ''
    tokensLength:int = len(tokens)

    def __init__(self, tokens:list[str], lineNumber:int):
        self.name = tokens[-1]
        self.operationAction = tokens[1]
        self.lineNumber = lineNumber
        self.tokens = tokens
        linestr = '|'.join(tokens)
        self.lines.append(linestr)
        self.timeStamp = self.tokens[0] if self.timeStamp is None else self.timeStamp
        self.tokensLength = len(tokens)

    def print(self):
        print(json.dumps(self.__dict__, indent=4, sort_keys=True))
