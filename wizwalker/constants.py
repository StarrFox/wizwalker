import ctypes
from enum import Enum


user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
gdi32 = ctypes.windll.gdi32
ntdll = ctypes.windll.ntdll


# Number of units covered in 1 second
WIZARD_SPEED = 580


type_format_dict = {
    "char": "<c",
    "signed char": "<b",
    "unsigned char": "<B",
    "bool": "?",
    "short": "<h",
    "unsigned short": "<H",
    "int": "<i",
    "unsigned int": "<I",
    "long": "<l",
    "unsigned long": "<L",
    "long long": "<q",
    "unsigned long long": "<Q",
    "float": "<f",
    "double": "<d",
}


# noinspection PyPep8
class Keycode(Enum):
    Left_mouse = 1
    Right_mouse = 2
    Control_break_processing = 3
    Middle_mouse = 4
    X1_mouse = 5
    X2_mouse = 6
    Undefined = 7
    BACKSPACE = 8
    TAB = 9
    CLEAR = 12
    ENTER = 13
    SHIFT = 16
    CTRL = 17
    ALT = 18
    PAUSE = 19
    CAPS_LOCK = 20
    ESC = 27
    SPACEBAR = 32
    PAGE_UP = 33
    PAGE_DOWN = 34
    END = 35
    HOME = 36
    LEFT_ARROW = 37
    UP_ARROW = 38
    RIGHT_ARROW = 39
    DOWN_ARROW = 40
    SELECT = 41
    PRINT = 42
    EXECUTE = 43
    PRINT_SCREEN = 44
    INS = 45
    DEL = 46
    HELP = 47
    ZERO = 48
    ONE = 49
    TWO = 50
    THREE = 51
    FOUR = 52
    FIVE = 53
    SIX = 54
    SEVEN = 55
    EIGHT = 56
    NINE = 57
    A = 65
    B = 66
    C = 67
    D = 68
    E = 69
    F = 70
    G = 71
    H = 72
    I = 73
    J = 74
    K = 75
    L = 76
    M = 77
    N = 78
    O = 79
    P = 80
    Q = 81
    R = 82
    S = 83
    T = 84
    U = 85
    V = 86
    W = 87
    X = 88
    Y = 89
    Z = 90
    Left_Windows = 91
    Right_Windows = 92
    Applications = 93
    Reserved = 252
    Computer_Sleep = 95
    Numeric_pad_0 = 96
    Numeric_pad_1 = 97
    Numeric_pad_2 = 98
    Numeric_pad_3 = 99
    Numeric_pad_4 = 100
    Numeric_pad_5 = 101
    Numeric_pad_6 = 102
    Numeric_pad_7 = 103
    Numeric_pad_8 = 104
    Numeric_pad_9 = 105
    Multiply = 106
    Add = 107
    Separator = 108
    Subtract = 109
    Decimal = 110
    Divide = 111
    F1 = 112
    F2 = 113
    F3 = 114
    F4 = 115
    F5 = 116
    F6 = 117
    F7 = 118
    F8 = 119
    F9 = 120
    F10 = 121
    F11 = 122
    F12 = 123
    F13 = 124
    F14 = 125
    F15 = 126
    F16 = 127
    F17 = 128
    F18 = 129
    F19 = 130
    F20 = 131
    F21 = 132
    F22 = 133
    F23 = 134
    F24 = 135
    NUM_LOCK = 144
    SCROLL_LOCK = 145
    Left_SHIFT = 160
    Right_SHIFT = 161
    Left_CONTROL = 162
    Right_CONTROL = 163
    Left_MENU = 164
    Right_MENU = 165
    Browser_Back = 166
    Browser_Forward = 167
    Browser_Refresh = 168
    Browser_Stop = 169
    Browser_Search = 170
    Browser_Favorites = 171
    Browser_Start_and_Home = 172
    Volume_Mute = 173
    Volume_Down = 174
    Volume_Up = 175
    Next_Track = 176
    Previous_Track = 177
    Stop_Media = 178
    Play_Pause_Media = 179
    Start_Mail = 180
    Select_Media = 181
    Start_Application_1 = 182
    Start_Application_2 = 183
    OEM_specific = 230
    IME_PROCESS = 229
    Attn = 246
    CrSel = 247
    ExSel = 248
    Erase_EOF = 249
    Play = 250
    Zoom = 251
    PA1 = 253
    Clear = 254
