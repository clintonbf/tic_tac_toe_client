# Adapted from: https://realpython.com/python-sockets/

"""
Copyright: Clinton Fernandes, February 2021
e-mail: clintonf@gmail.com
"""

import argparse
from struct import *
from game_data import *
from metadata import *

hosts = {
    'emerald': '24.85.240.252',
    'emerald-home': '192.168.0.10',
    'macair': '192.168.1.76',
    'clint': '74.157.196.143'
}

DEFAULT_HOST = hosts['macair']  # The server's hostname or IP address
DEFAULT_PORT = 42069  # The port used by the server
MAX_VERSION = 4
GAME_ID = 1


def print_message(message: dict):
    f"""
    Prints out a packet representation for debug purposes.
    
    :param message: {dict} representation of the data packet 
    :return: {None}
    """
    print(message["header"])
    print(message["payload"])


def get_game_object(protocol_version: int) -> GameData:
    f"""
    Gets the correct game_data object.

    :param protocol_version: {int} protocol version of game
    :return: {GameData}
    """
    if protocol_version == 1:
        return GameData()
    if protocol_version == 2:
        return GameData_v2()
    if protocol_version == 4:
        return GameData_a4()

    print("Invalid protocol specified")
    exit(1)


def get_header(s: socket) -> dict:
    f"""
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
    f"""
    Gets a message from the server.

    :param s: {socket} TCP socket
    :return: {dict} the header and payload data
    """
    header = get_header(s)

    payload_length = header["payload_length"]

    if payload_length != 0:
        payload = get_payload(s, header)
    else:
        payload = {"payload": None}

    message = {'header': header, 'payload': payload}

    return message


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
        print("You have been assigned player ID", game_data.get_uid())

        # Set identity_code
        message = get_message(s)

        if message["header"]["msg_type"] == STATUS_CODES.UPDATE.value:
            game_data.set_identity(message["payload"][0])

        print("Welcome player", chr(game_data.get_identity()))

        if game_data.get_identity() == IDs.X.value:
            turn_ok = False
            while not turn_ok:
                turn_ok = take_turn(game_data, s)

        # So, now we wait for an update message.
        while True:
            print("Waiting for player to play")
            server_message = get_message(s)

            msg_type = server_message["header"]["msg_type"]
            msg_context = server_message["header"]["context"]

            if msg_type == STATUS_CODES.UPDATE.value and msg_context == UPD_CONTEXTS.MOVE_MADE.value:
                adversarys_play = server_message["payload"][0]
                game_data.update_board(adversarys_play, game_data.get_adversary())
                game_data.print_board()

                turn_ok = False
                while not turn_ok:
                    turn_ok = take_turn(game_data, s)
            elif msg_type == STATUS_CODES.UPDATE.value and msg_context == UPD_CONTEXTS.END_OF_GAME.value:
                outcome = server_message["payload"][0]

                if outcome != OUTCOMES.WIN.value:
                    game_data.update_board(server_message["payload"][1], game_data.get_adversary())
                    game_data.print_board()

                print("You", EOF_MESSAGES[outcome])
                exit(0)
            else:
                print("Unexpected message received from server")
                print(server_message)


def take_turn(game_data: GameData_a4, s: socket):
    proposed_play = game_data.make_play(s, MESSAGES[CODES["INVITE"]])

    if proposed_play == 'Q':
        action = REQ_TYPES.META_ACTION.value
        context = REQ_CONTEXTS.QUIT.value
        payload_length = 0

        packet = pack("!LBBB", game_data.get_uid(), action, context, payload_length)
    else:
        action = REQ_TYPES.GAME_ACTION.value
        context = REQ_CONTEXTS.MAKE_MOVE.value
        payload = int(proposed_play)
        payload_length = 1

        packet = pack("!LBBBB", game_data.get_uid(), action, context, payload_length, payload)

    s.sendall(packet)

    # Now get confirmation from Server
    play_response = get_message(s)
    response_status = play_response["header"]["msg_type"]

    if response_status == STATUS_CODES.SUCCESS.value:
        game_data.update_board(proposed_play, game_data.get_identity())
        game_data.print_board()

        if proposed_play == 'Q':
            exit(0)

        return True
    else:  # TODO Handle errors
        print(RESPONSE_MESSAGES[response_status])
        return False


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
    payload_length = 2
    protocol_version = 1
    game_id = 1

    packet = [empty_byte, empty_byte, empty_byte, empty_byte, confirmation, rule_set, payload_length,
              protocol_version, game_id]

    s.sendall(bytes(packet))

    uid = get_uid(s)

    return uid


def get_uid(s: socket) -> int:
    f"""
    Gets the player's uid from the server.
    
    :param s: {socket} TCP socket connection 
    :return: {int}
    """

    # header = s.recv(2)  # Will this receive into a list of 2?
    msg_type = int.from_bytes(s.recv(1), 'big')
    msg_context = int.from_bytes(s.recv(1), 'big')
    payload_length = int.from_bytes(s.recv(1), 'big')
    uid = int.from_bytes(s.recv(payload_length), 'little')

    print("Payload length is", )

    if msg_type == 32:
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
    parser.add_argument("--port", help="server port #. Default = " + str(DEFAULT_PORT))

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
        port = DEFAULT_PORT

    play_game(args.host, port, version)


if __name__ == "__main__":
    main()
