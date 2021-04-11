# Adapted from: https://realpython.com/python-sockets/

"""
Copyright: Clinton Fernandes, February 2021
e-mail: clintonf@gmail.com
"""

import argparse
import enum
import socket
from game_data import GameData
from game_data import GameData_v2
from game_data import GameData_a4

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
    x = 88
    o = 79


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


# class RESPONSE_MESSAGES(enum.Enum):
#     CLIENT_ERRORS.INVALID_REQUEST = "Invalid request"
#     CLIENT_ERRORS.INVALID_UID = "Invalid uid supplied"
#     CLIENT_ERRORS.INVALID_TYPE.value = "Invalid msg_type"
#     CLIENT_ERRORS.INVALID_CONTEXT.value = "Invalid context supplied"
#     CLIENT_ERRORS.INVALID_PAYLOAD.value = "Invalid payload supplied"
#     GAME_ERRORS.INVALID_ACTION.value = "Invalid play"
#     GAME_ERRORS.ACTION_OUT_OF_TURN.value = "Not your turn"


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

hosts = {
    'emerald': '24.85.240.252',
    'emerald-home': '192.168.0.10',
    'macair': '192.168.1.76',
    'clint': '74.157.196.143'
}

HOST = hosts['macair']  # The server's hostname or IP address
# PORT = 65432  # The port used by the server
PORT = 40000  # The port used by the server
MAX_VERSION = 4
GAME_ID = 1


def convert_to_bytes(val, number_of_bytes: int = 1) -> bytes:
    return int(val).to_bytes(number_of_bytes, 'big')


def get_game_object(protocol_version: int) -> GameData:
    """
    Gets the correct game_data object.

    :param protocol_version: protocol version of game
    :return: GameData
    """
    if protocol_version == 1:
        return GameData()
    if protocol_version == 2:
        return GameData_v2()
    if protocol_version == 4:
        return GameData_a4()


def get_header(s: socket):
    """
    Gets the header from a TCP packet.

    :param s: {socket} TCP socket
    :return: {dict} details of the packet header
    """
    msg_type = int.from_bytes(s.recv(1), 'big')
    msg_context = int.from_bytes(s.recv(1), 'big')
    payload_length = int.from_bytes(s.recv(1), 'big')

    header = {"msg_type": msg_type, "context": msg_context, "payload_length": payload_length}

    return header


def get_payload(s: socket, header: dict) -> list:
    f"""
    Gets the payload from a server.
    
    :param s: {socket} TCP socket 
    :param header: {dict} the packet header 
    :return: {list} the payload message
    """

    payload = []

    for i in range(0, header['payload_length']):
        payload.append(int.from_bytes(s.recv(1), 'big'))

    return payload


def get_message(s: socket) -> dict:
    """
    Gets a message from the server.

    :param s: {socket} TCP socket
    :return: {dict} the header and payload data
    """
    header = get_header(s)
    payload = get_payload(s, header)

    d = {'header': header, 'payload': payload}

    return d


def play_game(host: str, port: int, protocol_version: int = 1):
    if protocol_version == 4:
        play_game_a4(host, port)
    else:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))

            proposed_play = None
            game_data = get_game_object(protocol_version)

            while True:
                server_message = s.recv(game_data.get_bytes_to_expect())
                message = int.from_bytes(server_message, 'big')

                if message == CODES["VERSION"]:
                    pass

                if message == CODES["WELCOME"]:
                    game_data.process_welcome(s, MESSAGES[CODES["WELCOME"]])
                    print(game_data)

                    if game_data.get_identity() == IDENTITIES["X"]:
                        proposed_play = game_data.make_play(s, MESSAGES[CODES["INVITE"]])

                if message == CODES["INVITE"]:
                    game_data.set_game_board(s)
                    game_data.print_board()

                    proposed_play = game_data.make_play(s, MESSAGES[CODES["INVITE"]])

                if message == CODES["INVALID"]:
                    print(MESSAGES[CODES["INVALID"]])
                    proposed_play = game_data.make_play(s, MESSAGES[CODES["INVITE"]])

                if message == CODES["ACCEPTED"]:
                    print(MESSAGES[CODES["ACCEPTED"]])
                    try:
                        game_data.set_play(proposed_play)
                    except IndexError:
                        # I have not idea what's happening
                        pass

                    proposed_play = None

                    game_data.print_board()

                if message == CODES["WIN"]:
                    print(MESSAGES[CODES["WIN"]])

                if message == CODES["LOSE"]:
                    print(MESSAGES[CODES["LOSE"]])

                if message == CODES["TIE"]:
                    print(MESSAGES[CODES["TIE"]])

                if message == CODES["DISCONNECT"]:
                    print(MESSAGES[CODES["DISCONNECT"]])


def play_game_a4(host: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        game_data = GameData_a4()

        game_data.set_uid(handshake(s))
        print("You have been assigned", game_data.get_uid())

        # Set identity_code
        message = get_message(s)
        if message["header"]["msg_type"] == STATUS_CODES.UPDATE:
            game_data.set_identity(message["payload"][0])

        if game_data.get_identity() == IDs.X:
            turn_ok = False
            while not turn_ok:
                turn_ok = take_turn(game_data, s)

        # So, now we wait for an update message.
        while True:
            server_message = get_message(s)

            if server_message["header"]["msg_type"] == STATUS_CODES.UPDATE:
                if server_message["header"]["context"] == UPD_CONTEXTS.MOVE_MADE:
                    adversarys_play = server_message["payload"][0]
                    game_data.update_board(adversarys_play, game_data.get_adversary())
                    game_data.print_board()

                    turn_ok = False
                    while not turn_ok:
                        turn_ok = take_turn(game_data, s)

                if server_message["header"]["context"] == UPD_CONTEXTS.END_OF_GAME:
                    outcome = server_message["payload"][0]

                    if outcome != OUTCOMES.WIN:
                        game_data.update_board(server_message["payload"][1], game_data.get_adversary())
                        game_data.print_board()

                    print("You", EOF_MESSAGES.outcome)
                    exit(0)


def take_turn(game_data: GameData_a4, s: socket):
    proposed_play = game_data.make_play(s, MESSAGES[CODES["INVITE"]])

    if proposed_play == 'Q':
        action = REQ_TYPES.META_ACTION.value
        context = REQ_CONTEXTS.QUIT.value
        payload = 0

        # packet = [
        #     game_data.get_uid(),
        #     REQ_TYPES.META_ACTION.value,
        #     REQ_CONTEXTS.QUIT.value,
        #     0
        # ]
    else:
        action = REQ_TYPES.GAME_ACTION.value
        context = REQ_CONTEXTS.MAKE_MOVE.value
        payload = int(proposed_play)

        # packet = [
        #     game_data.get_uid(),
        #     REQ_TYPES.GAME_ACTION.value,
        #     REQ_CONTEXTS.MAKE_MOVE.value,
        #     int(proposed_play)
        # ]

    packet = [game_data.get_uid(), action, context, 1, payload]

    send_packet(s, packet)  # Sending a payload on a quit. Technically there shouldn't be one

    # Now get confirmation from Server
    play_response = get_message(s)
    response_status = play_response["header"]["msg_type"]

    if response_status == STATUS_CODES.SUCCESS:
        game_data.update_board(proposed_play, game_data.get_identity())
        game_data.print_board()

        if proposed_play == 'Q':
            exit(0)

        return True
    else:
        print(RESPONSE_MESSAGES[response_status])
        return False


def create_play_packet(uid: int, msg_type: int, msg_context: int, proposed_play: int) -> [int]:
    uuid_str = str(uid)
    msg_type_str = str(msg_type)
    msg_context_str = str(msg_context)
    p_play_str = str(proposed_play)
    payload_length_str = str(len(p_play_str))

    packet_as_string = uuid_str + msg_type_str + msg_context_str + payload_length_str + p_play_str
    packet = packet_as_string.encode()

    # packet = []
    # packet.append(convert_to_bytes(uid, 4))
    # packet.append(convert_to_bytes(msg_type))
    # packet.append(convert_to_bytes(REQ_CONTEXTS.MAKE_MOVE))
    # payload_length = 1
    # packet.append(convert_to_bytes(payload_length_str))
    # packet.append(convert_to_bytes(proposed_play, payload_length_str))

    return packet


def send_packet(s: socket, packet: [int]):
    f"""

    :param s: {socket} TCP socket
    :param packet: {list} data to send
    :return: {None}
    """
    # Packet is composed of
    #   uuid (4 bytes)                  [0]
    #   status (1 byte)                 [1]
    #   context (1 byte)                [2]
    #   payload length (1 byte)         [3] # TTT moves are always 1 byte long. A convenient shortcut
    #   payload (payload_length bytes)  [4]

    s.sendall(packet[0].to_bytes(4, 'big'))

    for i in range(1, len(packet)):
        s.sendall(packet[i].to_bytes(1, 'big'))


def handshake(s: socket) -> int:
    f"""
    Sends the handshake for ttt.
    
    :param s: {socket}  
    :return: {int} uid of player
    """
    # Start with 4 'empty' bytes
    empty_byte = 0
    confirmation = 1
    rule_set = 1
    protocol_version = 1
    game_id = 1

    s.sendall(empty_byte.to_bytes(4, 'big'))
    s.sendall(confirmation.to_bytes(1, 'big'))
    s.sendall(rule_set.to_bytes(1, 'big'))
    s.sendall(protocol_version.to_bytes(1, 'big'))
    s.sendall(game_id.to_bytes(1, 'big'))

    uid = get_uid(s)

    return uid


def get_uid(s: socket) -> int:
    f"""
    Gets the player's uid from the server.
    
    :param s: {socket} TCP socket connection 
    :return: {int}
    """

    header = [s.recv(2)]  # Will this receive into a list of 2?

    payload_length = int.from_bytes(s.recv(1), 'big')
    uid = int.from_bytes(s.recv(payload_length), 'big')

    if int.from_bytes(header[0], 'big') == 32:
        msg_code = uid
        print(STATUS_MESSAGES[msg_code])
        exit(1)

    return uid


def get_version_options() -> str:
    string = "["

    for i in range(1, MAX_VERSION):
        string = string + str(i) + " | "

    string = string + str(MAX_VERSION) + "]"

    return string


def create_arguments() -> argparse:
    parser = argparse.ArgumentParser()

    protocol_help = "protocol version " + get_version_options() + ", default = 1, there is no version 3"

    parser.add_argument("host", help="server IP address")
    parser.add_argument("--version", help=protocol_help, type=int)
    parser.add_argument("--port", help="server port #. Default = " + str(PORT))

    return parser


def main():
    args = create_arguments().parse_args()
    try:
        version = int(args.version)
    except TypeError:
        version = 1

    if version not in (1, 2, 4):
        print("Invalid version")
        exit(1)

    try:
        port = int(args.port)
    except TypeError:
        port = PORT

    play_game(args.host, port, version)


if __name__ == "__main__":
    main()
