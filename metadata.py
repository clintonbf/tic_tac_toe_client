import enum

ENDIANNESS = 'little'

CODES = {
    "WELCOME": 1,
    "INVITE": 4,
    "INVALID": 5,
    "ACCEPTED": 6,
    "WIN": 7,
    "LOSE": 8,
    "TIE": 9,
    "DISCONNECT": 10,
    "VERSION": 11
}

MESSAGES = {
    1: "Welcome",
    4: "Your turn! What is your move?",
    5: "Invalid move. Try again",
    6: "Move accepted",
    7: "You win!",
    8: "You lose!",
    9: "Tie game",
    88: "You are X",
    79: "You are O",
    11: "Version number",
    10: "Opponent has disconnected. Please stand by."
}

IDENTITIES = {
    "X": 88,
    "O": 79,
    "x": 88,
    "o": 79
}


class IDs(enum.Enum):
    X = 88
    O = 79
    x = X
    o = O


class STATUS_CODES(enum.Enum):
    SUCCESS = 10
    UPDATE = 20
    CLIENT_INVALID_REQUEST = 30
    CLIENT_INVALID_UID = 31
    CLIENT_INVALID_TYPE = 32
    CLIENT_INVALID_CONTEXT = 33
    CLIENT_INVALID_PAYLOAD = 34
    SERVER_ERROR = 40
    INVALID_ACTION = 50
    ACTION_OUT_OF_TURN = 51


class REQ_TYPES(enum.Enum):
    CONFIRMATION = 1
    INFORMATION = 2
    META_ACTION = 3
    GAME_ACTION = 4


class CLIENT_ERRORS(enum.Enum):
    INVALID_REQUEST = 30
    INVALID_UID = 31
    INVALID_TYPE = 32
    INVALID_CONTEXT = 33
    INVALID_PAYLOAD = 34


class CLIENT_ERROR_MSGS(enum.Enum):
    INVALID_REQUEST = "Invalid request"
    INVALID_UID = "Invalid uid supplied"
    INVALID_TYPE = "Invalid msg_type"
    INVALID_CONTEXT = "Invalid context supplied"
    INVALID_PAYLOAD = "Invalid payload supplied"


class GAME_ERRORS(enum.Enum):
    INVALID_ACTION = 50
    ACTION_OUT_OF_TURN = 51


class GAME_ERROR_MSGS(enum.Enum):
    INVALID_ACTION = "Invalid play"
    ACTION_OUT_OF_TURN = "Not your turn"


RESPONSE_MESSAGES = {
    CLIENT_ERRORS.INVALID_REQUEST.value: "Invalid request",
    CLIENT_ERRORS.INVALID_UID.value: "Invalid uid supplied",
    CLIENT_ERRORS.INVALID_TYPE.value: "Invalid msg_type",
    CLIENT_ERRORS.INVALID_CONTEXT.value: "Invalid context supplied",
    CLIENT_ERRORS.INVALID_PAYLOAD.value: "Invalid payload supplied",
    GAME_ERRORS.INVALID_ACTION.value: "Invalid play",
    GAME_ERRORS.ACTION_OUT_OF_TURN.value: "Not your turn",
}


class REQ_CONTEXTS(enum.Enum):
    CONFIRM_RULESET = 1
    MAKE_MOVE = 1
    QUIT = 1


class UPD_CONTEXTS(enum.Enum):
    START_GAME = 1
    MOVE_MADE = 2
    END_OF_GAME = 3


class OUTCOMES(enum.Enum):
    WIN = 1
    LOSS = 2
    TIE = 3


class RPS_PLAYS(enum.Enum):
    ROCK = 1
    PAPER = 2
    SCISSORS = 3


# class EOF_MESSAGES(enum.Enum):
#     OUTCOMES.WIN = " win!"
#     OUTCOMES.LOSS = " lose!"
#     OUTCOMES.TIE = " tie!"

EOF_MESSAGES = {
    OUTCOMES.WIN.value: " win!",
    OUTCOMES.LOSS.value: "lose!",
    OUTCOMES.TIE.value: " tie!"
}

STATUS_MESSAGES = {
    10: "success",
    20: "update",
    30: "invalid_type",
    31: "invalid context",
    32: "invalid payload",
    40: "server error",
    50: "invalid action",
    51: "action out of turn"
}
