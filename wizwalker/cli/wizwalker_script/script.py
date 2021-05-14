from dataclasses import dataclass
from typing import Any, List, Optional, Tuple


@dataclass
class WizWalkerScript:
    loop: "Loop"
    battle: List["CombatAction"]
    move_steps: Optional[List["MoveSteps"]]


@dataclass
class Command:
    command_type: str
    param: Optional[str]


@dataclass
class Loop:
    commands: List[Command]
    iterations: Optional[int]


@dataclass
class CombatAction:
    action_type: str
    param: Optional[str]
    source: Optional[str]
    enchant: Optional[str]
    maybe_enchant: Optional[bool]


@dataclass
class MoveSteps:
    name: str
    steps: List[Tuple[int, int]]
