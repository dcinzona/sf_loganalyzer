import re

timestampPattern = re.compile("^(?P<time>\d{2}:\d{2}:\d{2}\.)")
class LogLine(object):
    operation = None
    stackOperation = None
    def __init__(self, lineString:str, lineNumber:int=0):
        isValid, line = LogLine.isValidLine(lineString.strip())
        if(isValid):
            self.line = line
            self.lineSplit = line.split("|")
            self.timeStamp = self.lineSplit[0]
            self.lineNumber = lineNumber
            self.additionalLines = None

    def addLine(self, line:str):
        if(self.additionalLines is None):
            self.additionalLines = [line]
            return self
        self.additionalLines.append(line)
        return self

    def isLimitsLine(self):
        return self.lineSplit[1] == 'LIMIT_USAGE_FOR_NS'

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

        # if(isValid == False and line.find(self.SEARCH_STRING) != -1 and prevLine.endswith('|LIMIT_USAGE_FOR_NS|(default)|')):
        #     return True, f'{prevLine}{line}'
        return isValid,line