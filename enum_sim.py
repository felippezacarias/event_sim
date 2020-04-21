from enum import Enum

class RecordType(Enum):
    STATE           = 1
    EVENT           = 2
    COMMUNICATION   = 3
    EXECUTED        = 4

#Global constant
GLOBAL_STATE_RUNNING = "Running"
GLOBAL_STATE_WAITING = "Wait/WaitAll"
GLOBAL_STATE_SYNC    = "Synchronization"
GLOBAL_STATE_OTHERS  = "Others"
GLOBAL_STATE_INIT      = "INIT"
GLOBAL_STATE_FINALIZE  = "FINALIZE"