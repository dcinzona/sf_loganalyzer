
import json
from pprint import pp

from Operations.EntryOrExit import EntryPoints

class kLimit:
    value:int = 0
    maxValue:int = 0
    def __init__(self, val, maxVal):
        self.value = val
        self.maxValue = maxVal

class LimitData:
    startlimits:object = None
    endlimits:object = None
    def __init__(self):
        self.startlimits = {}
        self.endlimits = {}

    def addLimit(self, start:bool, key:str, val:dict):
        if(start):
            self.startlimits[key] = val
        else:
            self.endlimits[key] = val

class Operation:
    OPSTACK:list = []
    name:str
    lines:list[str] = []
    lineNumber:int = 0
    timeStamp:str = None
    eventType:str = None
    eventId:str = None
    eventSubType:str = None
    operationAction:str = ''
    #tokensLength:int = 0
    limits:LimitData = None
    operations:list = []

    def __init__(self, tokens:list[str], lineNumber:int):
        self.name = None #tokens[-1]
        self.operationAction = tokens[1]
        self.lineNumber = lineNumber
        linestr = '|'.join(tokens)
        self.lines.append(linestr)
        self.timeStamp = tokens[0] if self.timeStamp is None else self.timeStamp
        #self.tokensLength = len(tokens)
        self.operations = []
        self.limits = LimitData()

    def print(self):
        #print(json.dumps(self, default=lambda x: x.__dict__, indent=4, sort_keys=True))

        pp(f'[{self.lineNumber}] {self.eventType}|{self.name}')
