from enum import Enum


class DuelPhase(Enum):
    starting = 0
    pre_planning = 1
    planning = 2
    pre_execution = 3
    execution = 4
    resolution = 5
    victory = 6
    ended = 7
    max = 10


class SigilInitiativeSwitchMode(Enum):
    none = 0
    reroll = 1
    switch = 2


class DuelExecutionOrder(Enum):
    sequential = 0
    alternating = 1


class PipAquiredByEnum(Enum):
    unknown = 0
    normal = 1
    power = 2
    normal_to_power_conversion = 4
    impede_pips = 5


class DelayOrder(Enum):
    any_order = 0
    first = 1
    second = 2
