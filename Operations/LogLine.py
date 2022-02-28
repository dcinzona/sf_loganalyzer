import copy
import re

timestampPattern = re.compile("^(?P<time>\d{2}:\d{2}:\d{2}\.)")


class Cluster(object):
    start: int
    end: int
    data: dict

    def __init__(self, start: int = 0, end: int = 0, data: dict = {}):
        self.start = start
        self.end = end
        # Or if you don't have lots of nested objects, data.copy()
        self.data = data.copy()


class LogLine(object):
    operation = None
    stackOperation = None

    def copy(self) -> 'LogLine':
        new_instance = LogLine(self.line, self.lineNumber)
        new_instance.__dict__.update(self.__dict__)
        #new_instance.additionalLines = copy.deepcopy(self.additionalLines)
        return new_instance

    def __init__(self, lineString: str, lineNumber: int = 0):
        self.line = lineString
        self.lineSplit = lineString.split("|")
        self.timeStamp = self.lineSplit[0]
        self.lineNumber = lineNumber
        self.additionalLines = []

    def addLine(self, line: str):
        self.additionalLines.append(line)
        return self

    def isLimitsLine(self):
        return self.lineSplit[1] == 'LIMIT_USAGE_FOR_NS'

    @staticmethod
    def isValidLine(line: str, idx: int = 0):
        isValid = timestampPattern.match(
            line) is not None and line.find('|') != -1
        return isValid, LogLine(line, idx)


class SOQLQueryLogLine(LogLine):

    SEARCH_STRING = "SOQL queries"

    def isValidLine(self, line):
        isValid = timestampPattern.match(
            line) is not None and line.find('|Validation:') == -1

        # if(isValid == False and line.find(self.SEARCH_STRING) != -1 and prevLine.endswith('|LIMIT_USAGE_FOR_NS|(default)|')):
        #     return True, f'{prevLine}{line}'
        return isValid, line
