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
