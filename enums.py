from enum import Enum


class TuningEnum(str, Enum):
    E = "Standard"
    Eb = "E Flat"


class StatusEnum(str, Enum):
    SUCCESS = "Success"
    ERROR = "Error"
    UNPROCESSED = "Unprocessed"
