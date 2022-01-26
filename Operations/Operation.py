import re
import Operations.LogData as LogData
timestampPattern = re.compile("^(?P<time>\d{2}:\d{2}:\d{2}\.)")


class Operation:
    name:str
    line:str
    lineNumber:int = 0
    lineSplit:list = []
    timeStamp:str
    eventType:str
    eventId:str
    eventSubType:str
    operations:list = []


class LogLine(Operation):

    def __init__(self, lineString:str, parentOperation:Operation=None):
        Operation.lineNum += 1
        isValid, line = self.isValidLine(lineString.strip())
        if(isValid):
            self.line = line
            self.lineSplit = line.split("|")
            self.lineNumber = Operation.lineNumber
            self.timeStamp = self.lineSplit[0]
            self.eventType = self.lineSplit[1]
            self.eventId = self.lineSplit[2]
            self.eventSubType = self.lineSplit[3]
            parentOperation.operations.append(self) if parentOperation else None
            LogData.logReversed.insert(0, self)

    
    def isValidLine(self, line):
        isValid = timestampPattern.match(line) is not None and line.find('|') != -1
        return isValid,line

class SOQLQueryLogLine(LogLine):

    SEARCH_STRING = "SOQL queries"

    def isValidLine(self, line):
        isValid = timestampPattern.match(line) is not None and line.find('|Validation:') == -1
        prevLine = LogData.logReversed[0] if len(LogData.logReversed) >= 1 else ''
        if(isValid == False and line.find(self.SEARCH_STRING) != -1 and prevLine.endswith('|LIMIT_USAGE_FOR_NS|(default)|')):
            return True, f'{prevLine}{line}'
        return isValid,line