from enum import Enum, IntFlag


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


class WindowStyle(IntFlag):
    has_back = 1
    scale_children = 2
    can_move = 4
    can_scroll = 16
    focus_locked = 64
    can_focus = 128
    can_dock = 32
    do_not_capture_mouse = 256
    is_transparent = 256
    effect_fadeid = 512
    effect_highlight = 1024
    has_no_border = 2048
    ignore_parent_scale = 4096
    use_alpha_bounds = 8192
    auto_grow = 16384
    auto_shrink = 32768
    auto_resize = 49152


class WindowFlags(IntFlag):
    visable = 1
    noclip = 2
    dock_outside = 131072
    dock_left = 128
    dock_top = 512
    dock_right = 256
    dock_bottom = 1024
    parent_size = 786432
    parent_width = 262144
    parent_height = 524288
    hcenter = 32768
    vcenter = 65536
    disabled = -2147483648
