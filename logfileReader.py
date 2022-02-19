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
    loglines:list[str]=[]

    @property
    def logReversed(self):
        return list(reversed(self.loglines))

    def __init__(self, **kwargs):
        self.options = dynamicDict(kwargs)
        self.logfile = self.options.logfile
        self.loglines = []
        self.lineCount = 0
        self.operations = []
        self.logpath = os.path.abspath(self.logfile)
        self.filename = os.path.basename(self.logpath)
        self.inputfileDir = os.path.dirname(os.path.abspath(self.logpath))
        self.factory = OperationFactory(operationTypes=self.options.types)

    def read(self):
        with open(self.logpath) as infile:
            self.lineCount=0
            for line in infile:
                self.lineCount += 1
                isValid, line = LogLine.isValidLine(line.strip())
                if(isValid):
                    self.loglines.append(line)
                    #self.factory.createOperation(LogLine(line, self.lineCount))
                    self.factory.createOrderedOperation(LogLine(line, self.lineCount))
        self.operations = self.factory.OPERATIONS

        if(self.options.get('debug', False)):
            openOps = 0
            for idx,op in enumerate(self.operations):
                if(op.finished == False):
                    openOps += 1
                    print(f'{idx} [{op.lineNumber}] "{op.name}" <{op.eventId}> is not finished')
            if(openOps > 0):
                print(f'{openOps} operations are not finished')
                #exit(1)

    def _sortStack(self):
        self.operations = self.factory.OPERATIONS # sorted(Operation.OPSTACK, key=lambda x: x["lineNumber"])
        return self.operations
