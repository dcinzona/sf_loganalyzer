from pprint import pp
from Operations.EntryOrExit import EntryPoints, ExitPoints
from Operations.Operation import Operation
import re

constructorPattern = re.compile(r"(\w+)\.\1\(\)$")


class MethodOperation(Operation):

    METHODSTACK: list = []
    color = "#0101FF"

    def __init__(self, ll):
        super(MethodOperation, self).__init__(ll)
        tokens = ll.lineSplit
        self.eventType = "APEX"
        # [id]MethodName
        self.eventId = f"{tokens[-3]}|{tokens[-2]}|{tokens[-1]}"
        self.eventSubType = "METHOD"
        self.isContructor(tokens)
        self.name = tokens[-1]
        if tokens[1] in ["METHOD_ENTRY", "CODE_UNIT_STARTED"]:
            # 15:09:44.547 (12548827536)|METHOD_ENTRY|[17]|01pr000000120Tt|SF86RecordSyncHelper.syncMilitaryToSect15(List<Military_Service__c>)
            self.lineNumber = ll.lineNumber
            self.appendToStack()
            # if(tokens[1] == 'CODE_UNIT_STARTED'):
            #     self.cluster = { 'name':self.name, 'start':self.lineNumber }

        if tokens[1] in ["METHOD_EXIT", "CODE_UNIT_FINISHED"]:
            d = self.findSelfinStack()
            if d is not None:
                self.update(d)
                self.finished = True
                # if(tokens[1] == 'CODE_UNIT_FINISHED'):
                #     self.cluster['end'] = ll.lineNumber if self.get('cluster', None) is not None else None
            else:
                pp(MethodOperation.METHODSTACK)
                print("^ METHODSTACK ^")
                pp(self.__dict__)
                raise Exception(
                    "Could not find matching MethodOperation in MethodOperation.METHODSTACK"
                )

    def appendToStack(self):
        MethodOperation.METHODSTACK.append(self)

    def findSelfinStack(self):
        if len(MethodOperation.METHODSTACK) == 0:
            raise Exception("MethodOperation.METHODSTACK is empty")
        # 15:09:44.547 (12548827536)|METHOD_EXIT|[17]|01pr000000120Tt|SF86RecordSyncHelper.syncMilitaryToSect15(List<Military_Service__c>)
        if (
            len(MethodOperation.METHODSTACK) == 1
            and self.operationAction == "METHOD_EXIT"
        ):
            return MethodOperation.METHODSTACK.pop()
        elif len(MethodOperation.METHODSTACK) >= 1:
            for x in MethodOperation.METHODSTACK[::-1]:
                if self.isMatch(x):
                    op = MethodOperation.METHODSTACK.pop(
                        MethodOperation.METHODSTACK.index(x)
                    )
                    return op

        pp(MethodOperation.METHODSTACK)
        pp(self.__dict__)
        exit()
        return None

    def isMatch(self, stackOp: Operation):
        if (
            self.operationAction == ExitPoints.METHOD_EXIT
            and stackOp.operationAction == EntryPoints.METHOD_ENTRY
        ):
            return self.eventId == stackOp.eventId
        elif (
            self.operationAction == ExitPoints.CODE_UNIT_FINISHED
            and stackOp.operationAction == EntryPoints.CODE_UNIT_STARTED
        ):
            return self.name == stackOp.name
        return False

    def isContructor(self, tokens: list):
        name = tokens[-1].strip()

        result = (
            constructorPattern.match(name) is not None if name.find(".") != -1 else True
        )
        # if(name.find('LeadDA.LeadDA()') > -1):
        #     print(result)
        #     print(constructorPattern.match(name))
        #     print(name)
        #     exit()
        if result:
            self.name = name.split(".")[0]
            self.eventSubType = "CONSTRUCTOR"
            self.eventId = f"CONSTRUCTOR:{self.name}"
        self.constructor = result
