from enum import Enum

class RecordType(Enum):
    STATE           = 1
    EVENT           = 2
    COMMUNICATION   = 3
    EXECUTED        = 4

#Global constant
GLOBAL_STATE_RUNNING = "Running"
GLOBAL_STATE_WAITING = "Wait/WaitAll"