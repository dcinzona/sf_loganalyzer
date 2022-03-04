"""
Run via command line: python3 readlog.py [logfile] [optional:outputfilecsv]
Requires Python 3.6 or higher
"""
import os
import sys
import re
import traceback

"""
15:05:12.412 (20450194753)|CODE_UNIT_STARTED|[EXTERNAL]|Flow:01Ir0000000HCxR
15:05:12.412 (20747809148)|CODE_UNIT_STARTED|[EXTERNAL]|Workflow:01Ir0000000HCxE
15:05:12.893 (21137018664)|CODE_UNIT_STARTED|[EXTERNAL]|Validation:PersonAccount:001r000000l8CIV
15:05:12.893 (21291331847)|CODE_UNIT_STARTED|[EXTERNAL]|01qr0000000AgQ9|AccountTrigger on Account trigger event AfterUpdate|__sfdc_trigger/AccountTrigger
15:06:18:343 CODE_UNIT_STARTED [EXTERNAL]|01qr0000000Agy3|DAForm5500Trigger on DA_Form_5500 trigger event AfterInsert|__sfdc_trigger/DAForm5500Trigger
"""
CODE_UNIT_STARTED = "CODE_UNIT_STARTED"
METHOD_ENTRY = "METHOD_ENTRY"
FLOW_START_INTERVIEW_BEGIN = "FLOW_START_INTERVIEW_BEGIN"
SEARCH_STRING = "SOQL queries"
FLOW_BULK_ELEMENT_LIMIT_USAGE = "FLOW_BULK_ELEMENT_LIMIT_USAGE"
FLOW_CREATE_INTERVIEW_END = "FLOW_CREATE_INTERVIEW_END"


class ComponentType:
    PB_STR = "|CODE_UNIT_STARTED|[EXTERNAL]|Workflow:"
    FLOW_STR = "|CODE_UNIT_STARTED|[EXTERNAL]|Flow:"
    # TRIG_STR = '|CODE_UNIT_STARTED|[EXTERNAL]|01qr'
    # APEX_STR = '|CODE_UNIT_STARTED|[EXTERNAL]|01pr'
    APEX_STR = "|CODE_UNIT_STARTED|[EXTERNAL]|01"
    PROCESS_BUILDER = "Process Builder"
    FLOW = "Flow"
    APEX = "Apex"


class readLog:
    header = "LineNumber,MethodOrFlow,Action,Delta,Total,FlowNode\n"
    pattern = re.compile(r"^(?P<time>\d{2}:\d{2}:\d{2}\.)")
    foundInLog = [header]
    logpath, filename, inputfileDir = "", "", ""
    flowMap = {}
    apexMap = {}
    logReversed = []
    runningActionType = None
    lineCount = 0
    currentNode = None

    def __init__(self, file=None, out=None) -> None:
        if not os.path.exists(file):
            raise (FileNotFoundError(f"File {file} not found"))
        self.logpath = os.path.abspath(file)

        self.filename = os.path.basename(self.logpath)
        self.inputfileDir = os.path.dirname(os.path.abspath(self.logpath))
        self.output_path = (
            os.path.abspath(out)
            if out
            else os.path.join(self.inputfileDir, f"{self.filename}.csv")
        )

    def isValidLine(self, line):
        prevLine = self.logReversed[0] if len(self.logReversed) >= 1 else ""
        isValid = (
            self.pattern.match(line) is not None and line.find("|Validation:") == -1
        )
        if (
            not isValid
            and line.find(SEARCH_STRING) != -1
            and prevLine.endswith("|LIMIT_USAGE_FOR_NS|(default)|")
        ):
            return True, f"{prevLine}{line}"
        return isValid, line

    def run(self):
        try:
            totalQueries = 0
            with open(self.logpath, "r", encoding="utf8") as infile:
                self.lineCount = 0
                prevSoqlQueriesCount = 0
                grouped = {}
                """
                Example log line that we are looking for:
                15:05:11.331 (19331387736)|FLOW_START_INTERVIEW_LIMIT_USAGE|SOQL queries: 49 out of 100
                """
                for line in infile:
                    self.lineCount += 1
                    count = self.lineCount
                    isValid, line = self.isValidLine(line.strip())
                    if not isValid:
                        # print(f'Skipping line {count}\n{line}')
                        continue

                    self.logReversed.insert(0, line)

                    codeUnit = self.processCodeUnit(line)
                    if codeUnit is not None:
                        # This is a code_unit_started line, no need to continue
                        # continue
                        pass

                    lineSplit = line.strip().split("|")
                    action = lineSplit[1]
                    lineLastElement = lineSplit[-1]
                    if lineLastElement.find(SEARCH_STRING) != -1:

                        # The last part of the line always has the SOQL queries text
                        soqltxt = lineLastElement.replace(" ******* CLOSE TO LIMIT", "")
                        # Split this part to a list "SOQL queries: 49 out of 100"
                        if soqltxt.find("Too many SOQL queries:") != -1:
                            totalQueries = 101
                        else:
                            try:
                                queryCt = int(soqltxt.split(" ")[-4::1][0])
                                totalQueries = (
                                    queryCt if queryCt > totalQueries else totalQueries
                                )
                                if totalQueries == 2:
                                    print(f"{self.lineCount}: {line}")
                            except Exception as e:
                                print(e)
                                print(lineSplit)
                                print(f"Error parsing SOQL queries: {soqltxt}")
                                exit()

                        if action == "FLOW_START_INTERVIEW_LIMIT_USAGE":
                            prevSoqlQueriesCount = totalQueries
                        # Skip if the query totals didn't change
                        if totalQueries <= prevSoqlQueriesCount:
                            totalQueries = prevSoqlQueriesCount
                            continue

                        # Capture the difference between the total count for this line and the previous total
                        delta = totalQueries - prevSoqlQueriesCount
                        if self.currentNode is not None:
                            flowEl = ""
                            if self.runningActionType in [
                                ComponentType.FLOW,
                                ComponentType.PROCESS_BUILDER,
                            ]:
                                self.currentNode, flowEl = self.getFlowName(lineSplit)

                            # append output CSV list with data
                            lntxt = f'{count},{self.runningActionType},"{self.currentNode}",+{delta},{totalQueries},"{flowEl}"\n'
                            self.foundInLog.append(lntxt)
                            # group results
                            gp = f"({self.runningActionType}) {self.currentNode}"  # .split('=>')[0].strip()
                            grouped[gp] = grouped.get(gp, 0) + delta
                        # store the total queries on this line to compare with the next find, to calculate the delta
                        prevSoqlQueriesCount = totalQueries
                        continue

                    if line.find("QueryLocatorIterator") == -1 and action in [
                        METHOD_ENTRY,
                        FLOW_START_INTERVIEW_BEGIN,
                        CODE_UNIT_STARTED,
                    ]:
                        self.currentNode = (
                            lineSplit[-1].replace("__sfdc_trigger/", "").strip()
                        )
                        continue
                    # END LINE LOOP

            # Log out to consol the grouped totals for each method / flow
            print("\n== Added more than 2 queries ==")
            sortedGroup = {
                k: v for k, v in sorted(grouped.items(), key=lambda item: item[1])
            }
            for key, value in sortedGroup.items():
                print(f"{key} added {value} queries") if value > 2 else None

            # DONE PROCESSING LOG
            print(
                f"\n== Summary ==\nFound { totalQueries } SOQL queries in {self.logpath}"
            )
            # Start the CSV writer process
            self.saveCsv()
            return totalQueries

        except Exception as e:
            print(f"\n== Error ==\n{e}\n")
            traceback.print_exc()
            print(
                f"\nLast Line: {self.lineCount}\n {self.logReversed[1]}\n {self.logReversed[0]}"
            )
            sys.exit(1)

    def getFlowName(self, lineSplit):
        actions = ["FLOW_VALUE_ASSIGNMENT", "FLOW_INTERVIEW_FINISHED"]
        flowLine = self.getLineWithAction(actions)
        if flowLine != "":
            flowLine = flowLine.split("|")
        else:
            print(f'{self.lineCount} - {"|".join(lineSplit)}')
            sys.exit(1)

        flowId = flowLine[2]
        if flowId in self.flowMap:
            self.runningActionType, flowName = self.flowMap[flowId]
            flowName = flowName.strip()
            flowEl = flowLine[3].strip()
            if (
                flowEl == flowName
                or self.runningActionType == ComponentType.PROCESS_BUILDER
            ):
                flowEl = ""
            return flowName, flowEl
        else:
            print(f"Flow {flowId} not found in map")
            sys.exit(1)

    def getLineWithAction(self, actions):
        for line in self.logReversed:
            lineAction = line.split("|")[1]
            if lineAction in actions:
                return line
        return ""

    def processCodeUnit(self, line):
        lineSplit = line.split("|")
        action = lineSplit[1]
        codeUnitMap = {
            ComponentType.PROCESS_BUILDER: ComponentType.PB_STR,
            ComponentType.FLOW: ComponentType.FLOW_STR,
            ComponentType.APEX: ComponentType.APEX_STR,
        }

        for k, v in codeUnitMap.items():
            if line.find(v) != -1:
                self.runningActionType = k
                return self.runningActionType

        if action == FLOW_CREATE_INTERVIEW_END:
            # have to check the previous line to determine if this is a flow or a process builder
            # seems like process builders all have the last element in the previous line starting with 301r
            # flows don't have that last element, so they start with 300r
            isPB = self.logReversed[1].split("|")[-1].strip().startswith("301r")
            self.runningActionType = (
                ComponentType.PROCESS_BUILDER if isPB else ComponentType.FLOW
            )
            self.flowMap[lineSplit[2]] = self.runningActionType, lineSplit[3]

        elif action == METHOD_ENTRY:
            self.runningActionType = ComponentType.APEX
            self.buildApexMap(lineSplit)

        return None

    def buildApexMap(self, lineSplit):
        lastElement = lineSplit[-1]
        if lastElement.find("__sfdc_trigger/") != -1:
            trigger = lastElement.split("/")[-1]
            eventText = lineSplit[-2].split("event ")[-1]
            lastElement = f"{trigger} {eventText}"
        codeUnit = (
            f"{lastElement}" if not lastElement.startswith("Validation:") else None
        )
        if (
            codeUnit is not None
            and lastElement.find("flow:") == -1
            and lineSplit[2] == "[EXTERNAL]"
        ):
            apexClassId = lineSplit[3]
            if apexClassId not in self.apexMap:
                self.apexMap[apexClassId] = codeUnit

    def saveCsv(self):
        # Make the output path if it doesn't exist (and any intermediary directories)
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        # We handle new lines using \n in our processing method.
        with open(self.output_path, "w", newline=None) as outfile:
            for line in self.foundInLog:
                outfile.write(line)
        # Let the user know where the file was saved
        print(f"Saved to {self.output_path}")
