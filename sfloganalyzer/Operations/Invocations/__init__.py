from .CalloutOperation import CalloutOperation
from .DMLOperation import DMLOperation
from .ExecutionOperation import ExecutionOperation
from .FlowOperation import FlowOperation
from .MethodOperation import MethodOperation
from .TriggerOperation import TriggerOperation
from .FatalError import FatalErrorOp

FatalErrorOperation = FatalErrorOp
ExceptionOperation = FatalErrorOp
__all__ = (
    "CalloutOperation",
    "DMLOperation",
    "ExecutionOperation",
    "FatalErrorOp",
    "FlowOperation",
    "MethodOperation",
    "TriggerOperation",
    FatalErrorOperation,
    ExceptionOperation,
)
