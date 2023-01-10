from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class SystemStatus:
    status: int
    pd_protection: Tuple[bool, ...] = field(init=False)
    temperature_protection: Tuple[bool, ...] = field(init=False)
    fault: bool = field(init=False)

    def __post_init__(self):
        pd_protection_bits = [4, 5, 6, 7]
        temperature_protection_bits = [8, 9, 10, 11, 12]

        pd_protection = tuple(
            bool(self.status >> pdb & 1) for pdb in pd_protection_bits
        )
        object.__setattr__(self, "pd_protection", pd_protection)

        temperature_protection = tuple(
            bool(self.status >> tpb & 1) for tpb in temperature_protection_bits
        )
        object.__setattr__(self, "temperature_protection", temperature_protection)

        object.__setattr__(self, "fault", self.status != 0)


@dataclass(frozen=True)
class DriverUnlock:
    driver_unlock: int
    driver_enable_control: Tuple[bool, ...] = field(init=False)
    driver_enable_flag: Tuple[bool, ...] = field(init=False)
    interlock: bool = field(init=False)

    def __post_init__(self):
        driver_enable_control = tuple(
            bool(self.driver_unlock >> bi & 1) for bi in range(3)
        )
        driver_enable_flag = tuple(
            bool(self.driver_unlock >> bi & 1) for bi in range(3, 6)
        )
        interlock = bool(self.driver_unlock >> 6 & 1)
        object.__setattr__(self, "driver_enable_control", driver_enable_control)
        object.__setattr__(self, "driver_enable_flag", driver_enable_flag)
        object.__setattr__(self, "interlock", interlock)


@dataclass(frozen=True)
class PDStatus:
    status: int
    sampling_enable: bool = field(init=False)
    hardware_protection: bool = field(init=False)
    upper_limit_enabled: bool = field(init=False)
    lower_limit_enabled: bool = field(init=False)
    hardware_protection_event: bool = field(init=False)
    upper_limit_event: bool = field(init=False)
    lower_limit_event: bool = field(init=False)
    fault: bool = field(init=False)

    def __post_init__(self):
        for idf, field in enumerate(self.__dataclass_fields__):
            if field in ["status", "fault"]:
                continue
            idf -= 1
            object.__setattr__(self, field, bool(self.status >> idf & 1))

        object.__setattr__(
            self,
            "fault",
            self.hardware_protection_event
            | self.upper_limit_event
            | self.lower_limit_event,
        )


@dataclass(frozen=True)
class PrecilaserStatus:
    status: int
    endian: str = "big"
    stable: bool = field(init=False)
    system_status: SystemStatus = field(init=False)
    driver_unlock: DriverUnlock = field(init=False)
    driver_current: Tuple[float, ...] = field(init=False)
    pd_value: Tuple[int, ...] = field(init=False)
    pd_status: Tuple[PDStatus, ...] = field(init=False)
    temperatures: Tuple[float, ...] = field(init=False)

    def __post_init__(self):
        byte_index = 0
        status_bytes = self.status.to_bytes(64, self.endian)

        # get the stable bit
        object.__setattr__(self, "stable", bool(status_bytes[byte_index]))

        # get the system status
        byte_index = 3
        system_status_int = int.from_bytes(
            status_bytes[byte_index : byte_index + 2], self.endian
        )
        system_status = SystemStatus(system_status_int)
        object.__setattr__(self, "system_status", system_status)

        # get the driver unlock register
        object.__setattr__(self, "driver_unlock", DriverUnlock(status_bytes[4]))

        # get currents in A
        byte_index = 7
        driver_current = tuple(
            int.from_bytes(status_bytes[bi : bi + 2], self.endian) / 100
            for bi in range(byte_index, byte_index + 3 * 2, 2)
        )
        object.__setattr__(self, "driver_current", driver_current)

        # get the pd readout
        byte_index = 28
        pd_value = tuple(
            int.from_bytes(status_bytes[bi : bi + 2], self.endian)
            for bi in range(byte_index, byte_index + 5 * 2, 2)
        )
        object.__setattr__(self, "pd_value", pd_value)

        # get the pd status
        byte_index = 36
        pd_status = tuple(
            PDStatus(int.from_bytes(status_bytes[bi : bi + 1], self.endian))
            for bi in range(byte_index, byte_index + 4)
        )
        object.__setattr__(self, "pd_status", pd_status)

        # get the temperatures in C
        byte_index = 42
        temperatures = tuple(
            int.from_bytes(status_bytes[bi : bi + 2], self.endian) / 100
            for bi in range(byte_index, byte_index + 4 * 2, 2)
        )
        object.__setattr__(self, "temperatures", temperatures)
