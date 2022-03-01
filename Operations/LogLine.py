import re

timestampPattern = re.compile(r"^(?P<time>\d{2}:\d{2}:\d{2}\.)")


class LogLine(object):
    operation = None
    stackOperation = None

    def copy(self) -> 'LogLine':
        new_instance = LogLine(self.line, self.lineNumber)
        new_instance.__dict__.update(self.__dict__)
        # new_instance.additionalLines = copy.deepcopy(self.additionalLines)
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

    def isValidLine(self, line, prevLine: LogLine, idx: int = 0):
        isValid = timestampPattern.match(
            line) is not None and line.find('|Validation:') == -1

        if(isValid is False and line.find(self.SEARCH_STRING) != -1
           and prevLine.endswith('|LIMIT_USAGE_FOR_NS|(default)|')):
            return True, f'{prevLine}{line}'
        return isValid, line
