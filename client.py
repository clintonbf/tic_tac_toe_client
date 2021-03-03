# Adapted from: https://realpython.com/python-sockets/

"""
Copyright: Clinton Fernandes, February 2021
e-mail: clintonf@gmail.com
"""

import argparse
import socket
import sys
from game_data import GameData
from game_data import GameData_v2

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
    11: "Version number"
}

IDENTITIES = {
    "X": 88,
    "O": 79
}

hosts = {
    'emerald': '24.85.240.252',
    'emerald-home': '192.168.0.10',
    'macair': '192.168.1.76',
    'clint': '74.157.196.143'
}

HOST = hosts['macair']  # The server's hostname or IP address
PORT = 65432  # The port used by the server
MAX_VERSION = 2


def get_game_object(protocol_version: int = 1) -> GameData:
    """
    Gets the correct game_data object.

    :param protocol_version: protocol version of game
    :return: GameData
    """
    if protocol_version == 1:
        return GameData()
    if protocol_version == 2:
        return GameData_v2()


def play_game(host: str, port: int, protocol_version: int = 1):
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

                if game_data.get_identity() == IDENTITIES["X"]:
                    proposed_play = make_play(s, MESSAGES[CODES["INVITE"]])

            if message == CODES["INVITE"]:
                game_data.set_game_board(update_board(s))
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


def play_protocol_one(s):
    proposed_play = None
    game_data = GameData()

    while True:
        server_message = s.recv(game_data.get_bytes_to_expect())
        message = int.from_bytes(server_message, 'big')

        if message == CODES["VERSION"]:
            pass

        if message == CODES["WELCOME"]:
            print(MESSAGES[CODES["WELCOME"]])
            game_data.set_identity(int.from_bytes(s.recv(game_data.get_bytes_to_expect()), 'big'))
            print("You are player", chr(game_data.get_identity()))

            if game_data.get_identity() == IDENTITIES["X"]:
                proposed_play = make_play(s, MESSAGES[CODES["INVITE"]])

        if message == CODES["INVITE"]:
            game_data.set_game_board(update_board(s))
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


def play_protocol_two(s):
    proposed_play = None
    game_data = GameData_v2()
    number_of_bytes = 1

    while True:
        server_message = s.recv(game_data.get_bytes_to_expect())
        message = int.from_bytes(server_message, 'big')

        if message == CODES["VERSION"]:
            pass

        if message == CODES["WELCOME"]:
            print(MESSAGES[CODES["WELCOME"]])
            game_data.set_game_id(int.from_bytes(s.recv(number_of_bytes), 'big'))
            game_data.set_identity(int.from_bytes(s.recv(number_of_bytes), 'big'))
            print("You are player", chr(game_data.get_identity()))

            if game_data.get_identity() == IDENTITIES["X"]:
                proposed_play = make_play(s, MESSAGES[CODES["INVITE"]])

        if message == CODES["INVITE"]:
            game_data.set_game_board(update_board(s))
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
                # I have no idea what's happening
                pass

            proposed_play = None

            game_data.print_board()

        if message == CODES["WIN"]:
            print(MESSAGES[CODES["WIN"]])

        if message == CODES["LOSE"]:
            print(MESSAGES[CODES["LOSE"]])

        if message == CODES["TIE"]:
            print(MESSAGES[CODES["TIE"]])


def update_board(s) -> list:
    """
    Updates the local game board.

    :param s: socket
    :return: list
    """
    play = s.recv(9)

    board_bytes = play.decode()

    new_board = [ord(board_bytes[i:i + 1]) for i in range(0, len(board_bytes), 1)]

    return new_board


def make_play(s: socket, invitation: str) -> int:
    """
    Makes a play.

    :param s: socket
    :param invitation: invitation to display to user
    :return: int
    """
    proposed_play = input(invitation)

    play_ord = ord(proposed_play)
    s.sendall(play_ord.to_bytes(1, 'big'))

    return int(proposed_play)


def get_version_options() -> str:
    string = "["

    for i in range(1, MAX_VERSION):
        string = string + str(i) + " | "

    string = string + str(MAX_VERSION) + "]"

    return string


def create_arguments() -> argparse:
    parser = argparse.ArgumentParser()

    protocol_help = "protocol version " + get_version_options() + ", default = 1"

    parser.add_argument("host", help="server IP address")
    parser.add_argument("--version", help=protocol_help, type=int)
    parser.add_argument("--port", help="server port #. Default = " + str(PORT))

    return parser


def main():
    args = create_arguments().parse_args()
    version = args.version or 1
    port = args.port or PORT

    play_game(args.host, port, version)


if __name__ == "__main__":
    main()
