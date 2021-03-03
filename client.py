# Adapted from: https://realpython.com/python-sockets/

"""
Copyright: Clinton Fernandes, February 2021
e-mail: clintonf@gmail.com
"""

import socket
import sys
from game_data import GameData
from game_data_v_2 import GameData_v2

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

def play_game(protocol_version: int = 1):
     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        proposed_play = None
        game_data = get_game_object(protocol_version)
        game_data.get_version()

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

            proposed_play =  game_data.make_play(s, MESSAGES[CODES["INVITE"]])

        if message == CODES["INVALID"]:
            print(MESSAGES[CODES["INVALID"]])
            proposed_play =  game_data.make_play(s, MESSAGES[CODES["INVITE"]])

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


def get_connection_args(test: bool = False) -> tuple:
    """
    Gets the command line arguments.

    :param test: whether or not to use in-script defined host and port settings
    :return:
    """
    if test:
        info = (HOST, PORT)
        return info

    host = sys.argv[1]
    port = int(sys.argv[2])

    info = (host, port)
    return info


def main():
    connection_args = get_connection_args()
    protocol_version = None

    if len(connection_args) != 2 and len(connection_args) != 3:
        print("Usage: python client_game.py <host> <port> [<protocol version>]")
        exit(1)

    if len(sys.argv) == 4:
        protocol_version = int(sys.argv[3])

    play_game(protocol_version)

if __name__ == "__main__":
    main()
