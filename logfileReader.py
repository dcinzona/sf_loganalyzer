from pprint import pp
import sys, os, re, traceback
from Operations.LogData import LogData
from Operations.LogLine import LogLine
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

    def read(self):
        with open(self.logpath) as infile:
            self.lineCount=0
            for line in infile:
                self.lineCount += 1
                isValid, line = LogLine.isValidLine(line.strip())
                if(isValid):
                    self.logReversed.insert(0, line)
                    ll = LogLine(line, self.lineCount)
                    # ll.stackOperation = LogData().getStack().peek() if LogData().getStack().is_empty() == False else None
                    op = OperationFactory.createOperation(ll)
        
        for op in [f'[{x["lineNumber"]}] {x["eventType"]} | {x["name"]}' for x in Operation.OPSTACK]:
            #pp(op.__dict__)
            pp(op)
        print(len(Operation.OPSTACK))
