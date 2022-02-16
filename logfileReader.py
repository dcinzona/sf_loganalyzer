from pprint import pp
import sys, os, re, traceback
from Operations.Invocations.FatalError import FatalErrorOp
from Operations.LogData import LogData
from Operations.LogLine import LogLine
from Operations.OpUtils import dynamicDict
from Operations.Operation import Operation
from Operations.OperationFactory import OperationFactory


class reader:

    lineCount:int=0
    logReversed:list=[]

    def __init__(self, logfile):
        self.logfile = logfile
        self.logReversed = []
        self.lineCount = 0
        self.operations = []
        self.logpath = os.path.abspath(logfile)
        self.filename = os.path.basename(self.logpath)
        self.inputfileDir = os.path.dirname(os.path.abspath(self.logpath))
        self.factory = OperationFactory()

    def read(self):
        with open(self.logpath) as infile:
            self.lineCount=0
            for line in infile:
                self.lineCount += 1
                isValid, line = LogLine.isValidLine(line.strip())
                if(isValid):
                    self.logReversed.insert(0, line)
                    ll = LogLine(line, self.lineCount)
                    op = self.factory.createOperation(ll)
        
        self.operations = self.factory.OPERATIONS

    # def _defineStackProcessMap(self):
    #     self.operations = self._sortStack()
    #     if(len(self.operations) == 0):
    #         raise Exception("No operations found in the log file")
    #     for idx, op in enumerate(self.operations):
    #         op['idx'] = idx

    #     self.stackProcessMap = {}
    #     for op in self.operations:
    #         uid = op["eventType"] + "|" + op["name"]
    #         if(uid in self.stackProcessMap):
    #             self.stackProcessMap[uid].append(op)
    #         else:
    #             self.stackProcessMap[uid] = [op]
    #     return self.stackProcessMap
        

    def _sortStack(self):
        self.operations = self.factory.OPERATIONS # sorted(Operation.OPSTACK, key=lambda x: x["lineNumber"])
        return self.operations
