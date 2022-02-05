
from readlog import METHOD_ENTRY


class EntryPoints:
    CODE_UNIT_STARTED = "CODE_UNIT_STARTED" # Entry point for Apex and Flows
    FLOW_START = 'FLOW_START_INTERVIEW_BEGIN'
    FLOW_START_INTERVIEW_LIMIT_USAGE = 'FLOW_START_INTERVIEW_LIMIT_USAGE'
    METHOD_ENTRY = 'METHOD_ENTRY'
    FLOW_CREATE_INTERVIEW_BEGIN = 'FLOW_CREATE_INTERVIEW_BEGIN' #Process Builder will split on '|' to 5 element lists, Flows = 4
    ENTRY_POINTS = [FLOW_START, FLOW_CREATE_INTERVIEW_BEGIN, METHOD_ENTRY]
    
class ExitPoints:
    FLOW_INTERVIEW_FINISHED = 'FLOW_INTERVIEW_FINISHED'
    CODE_UNIT_FINISHED = 'CODE_UNIT_FINISHED'
    FLOW_CREATE_INTERVIEW_END = 'FLOW_CREATE_INTERVIEW_END' #Last element has the name of the flow / process builde
    FLOW_END = 'FLOW_START_INTERVIEW_END'
    FLOW_INTERVIEW_FINISHED_LIMIT_USAGE = 'FLOW_INTERVIEW_FINISHED_LIMIT_USAGE'
    METHOD_EXIT = 'METHOD_EXIT'
    EXIT_POINTS = [FLOW_INTERVIEW_FINISHED, CODE_UNIT_FINISHED, FLOW_CREATE_INTERVIEW_END, METHOD_EXIT]


class EntryOrExit:
    ENTRY='ENTRY'
    EXIT='EXIT'
    BEGIN='BEGIN'
    END='END'
    STARTED='STARTED'
    FINISHED='FINISHED'
    REQUEST='REQUEST'
    RESPONSE='RESPONSE'
    ALL= EntryPoints.ENTRY_POINTS + ExitPoints.EXIT_POINTS + [EntryPoints.FLOW_START_INTERVIEW_LIMIT_USAGE, ExitPoints.FLOW_INTERVIEW_FINISHED_LIMIT_USAGE]

