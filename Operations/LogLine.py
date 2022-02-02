
from Operations.LogData import LogData
import re
timestampPattern = re.compile("^(?P<time>\d{2}:\d{2}:\d{2}\.)")
class LogLine():
    operation = None
    stackOperation = None
    def __init__(self, lineString:str, lineNumber:int=0):
        isValid, line = LogLine.isValidLine(lineString.strip())
        if(isValid):
            self.line = line
            self.lineSplit = line.split("|")
            self.timeStamp = self.lineSplit[0]
            #self.eventType = self.lineSplit[1]
            #self.eventId = self.lineSplit[2]
            #self.eventSubType = self.lineSplit[3]
            self.lineNumber = lineNumber

            

    
    @staticmethod
    def isValidLine(line):
        isValid = timestampPattern.match(line) is not None and line.find('|') != -1
        return isValid,line


    @property
    def isEntrypoint(self):
        return self.eventType == "CODE_UNIT_STARTED" or self.eventType == "FLOW_START"
        
    @property
    def isExitpoint(self):
        return self.eventType == "CODE_UNIT_FINISHED" or self.eventType == "FLOW_INTERVIEW_FINISHED"


class SOQLQueryLogLine(LogLine):

    SEARCH_STRING = "SOQL queries"

    def isValidLine(self, line):
        isValid = timestampPattern.match(line) is not None and line.find('|Validation:') == -1
        prevLine = LogData.logReversed[0] if len(LogData.logReversed) >= 1 else ''
        if(isValid == False and line.find(self.SEARCH_STRING) != -1 and prevLine.endswith('|LIMIT_USAGE_FOR_NS|(default)|')):
            return True, f'{prevLine}{line}'
        return isValid,line