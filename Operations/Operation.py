
from abc import ABC
import json
from pprint import pp

import traceback
from Operations.EntryOrExit import EntryOrExit, EntryPoints, ExitPoints
from Operations.OpUtils import dynamicDict

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


class Operation(dynamicDict):
    OPSTACK:list = []
    name:str = ''
    lines:list[str] = []
    lineNumber:int = 0
    timeStamp:str = None
    eventType:str = None
    eventId:str = None
    eventSubType:str = None
    operationAction:str = ''
    #tokensLength:int = 0
    limits:LimitData = LimitData()
    operations:list = []
    LAST_OPERATION:dict = None

    def __init__(self, ll):
        #self.name = None #tokens[-1]
        tokens = ll.lineSplit
        self.operationAction = tokens[1]
        self.lineNumber = ll.lineNumber
        linestr = ll.line
        self.lines.append(linestr)
        self.timeStamp = tokens[0] if self.timeStamp is None else self.timeStamp
       

    def updateData(self, opDict:dict):        
        self.update(opDict)

    def isEntry(self):
        return self.operationAction in EntryPoints.ENTRY_POINTS
        
    def isExit(self):
        return self.operationAction in ExitPoints.EXIT_POINTS

    def appendTo(cls, opStack:list):
        opStack.append(cls.__dict__.copy())

    @staticmethod
    def print(cls, msg=None):
        #print(json.dumps(self, default=lambda x: x.__dict__, indent=4, sort_keys=True))
        try:
            ln = f'[{cls.lineNumber}] {cls.eventType}|{cls.name}' if msg is None else f'[{cls.lineNumber}] {msg}'
            print(ln)
        except Exception as e:
            pp(traceback.format_exc())
            print(cls.lineNumber)
            print(cls.__class__)
            exit(e)


    @staticmethod
    def findSelfinStack(op, stack:list[dict], eventIdOnly=False) -> dict:
        if(len(stack) > 0):
            for i in range(len(stack)-1, -1, -1):
                sop = stack[i]
                if(sop.get('eventId') == op.eventId):
                    return stack.pop(i)
                if(eventIdOnly == False):
                    try:
                        if(sop.get('name') == op.name and sop.get('eventType') == op.eventType, sop.get('eventSubType') == op.eventSubType):
                            return stack.pop(i)
                        # if(sop.eventType == op.eventType and sop.eventSubType == op.eventSubType):
                        #     return sop,i
                    except Exception:
                        print(traceback.format_exc())
                        print(op)
                        pp(stack[i])
                        exit()
        print(f'{op.name} not found in stack :(')
        pp(stack)
        pp(op)
        return None

