from enum import Enum, auto


class PrecilaserCommand(Enum):
    AMP_ENABLE = b"\x30"
    AMP_SET_CURRENT = b"\xa1"
    AMP_POWER_STABILIZATION = b"\x47"
    AMP_STATUS = b"\x04"
    SEED_STATUS = b"\xA9"
    SEED_SET_TEMP = b"\xA5"
    SEED_SET_VOLTAGE = b"\xAE"


class PrecilaserReturn(Enum):
    AMP_ENABLE = b"\x40"
    AMP_SET_CURRENT = b"\x41"
    AMP_POWER_STABILIZATION = b"\x44"
    SEED_STATUS = b"\xB7"
    SEED_SET_TEMP = b"\xB5"
    SEED_SET_VOLTAGE = b"\xBE"


class PrecilaserMessageType(Enum):
    COMMAND = auto()
    RETURN = auto()


class PrecilaserDeviceType(Enum):
    AMP = auto()
    SEED = auto()
