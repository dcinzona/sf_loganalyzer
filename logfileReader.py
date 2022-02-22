from pprint import pp
import sys, os, re, traceback
from Operations.Invocations.FatalError import FatalErrorOp
from Operations.Invocations.TriggerOperation import TriggerOperation
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
        self.factory = OperationFactory(**self.options)
        self.operations = self.factory.OPERATIONS
        self.limitUsageLines = []

    def read(self):
        with open(self.logpath) as infile:
            self.lineCount=0
            self.lastValidLine = None
            self.processedInvalid = False
            self.getNextCodeUnitFinished = False
            for line in infile:
                self.lineCount += 1
                isValid, line = LogLine.isValidLine(line.strip())
                if(isValid):
                    if(self.processedInvalid == True):
                        #finished processing lines that did not have a timestamp and now processing the next valid line 
                        # (so we need to reset the flag and process the last valid line if it's a limits line)
                        self.processedInvalid = False
                        if(self.lastValidLine.isLimitsLine()):
                            self.limitUsageLines.append(self.lastValidLine)
                            self.getNextCodeUnitFinished = True                            
                            pass

                    ll = LogLine(line, self.lineCount)
                    self.lastValidLine = ll;
                    self.loglines.append(line)
                    self.factory.createOrderedOperation(ll)

                    if(self.getNextCodeUnitFinished and ll.lineSplit[1] == 'CODE_UNIT_FINISHED' and len(self.limitUsageLines) > 0):
                        self.getNextCodeUnitFinished = False
                        op = self.getLastOperationByAttribute("name", ll.lineSplit[2])
                        limitsLine = self.limitUsageLines.pop()
                        op.processLimits(limitsLine) if op is not None else None

                    self.processedInvalid = False

                else:
                    #line didn't have a timestamp or pipe character
                    if(self.lastValidLine is not None):
                        self.lastValidLine.addLine(line)
                        self.processedInvalid = True
                        

        if(self.options.get('debug', False)):
            openOps = 0
            opCountsByType = {}
            for idx,op in enumerate(self.operations):
                if(op.finished == False):
                    openOps += 1
                    print(f'{idx} [{op.lineNumber}] "{op.name}" <{op.eventId}> is not finished')
                opCountsByType.setdefault(op.__class__.__name__, 0)
                opCountsByType[op.__class__.__name__] += 1

            if(openOps > 0):
                print(f'{openOps} operations are not finished')

            print('\nCounts by type of operation:')
            for k,v in opCountsByType.items():
                print(f'{k}: {v}')
                #exit(1)


    def getLastOperationByAttribute(self, attr, value):
        for op in reversed(self.operations):
            if(getattr(op, attr) == value):
                return op
        return None

    def _sortStack(self):
        self.operations = self.factory.OPERATIONS # sorted(Operation.OPSTACK, key=lambda x: x["lineNumber"])
        return self.operations
