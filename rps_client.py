import argparse
from struct import *
from game_data import *
from metadata import *

MAX_VERSION = 4
DEFAULT_PORT = 2034
GAME_ID = 2


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


def play_game(host: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        game_data = GameData_a4()

        game_data.set_uid(handshake(s))
        print("You have been assigned player ID", game_data.get_uid())

        message = get_message(s)

        if message["header"]["msg_type"] == STATUS_CODES.UPDATE.value:
            print("Welcome player")

        turn_ok = False
        while not turn_ok:
            turn_ok = take_turn(game_data, s)

        while True:
            print("Waiting for player to play")
            server_message = get_message(s)

            msg_type = server_message["header"]["msg_type"]
            msg_context = server_message["header"]["context"]

            if msg_type == STATUS_CODES.UPDATE.value and msg_context == UPD_CONTEXTS.MOVE_MADE.value:
                adversarys_play = server_message["payload"][0]

                turn_ok = False
                while not turn_ok:
                    turn_ok = take_turn(game_data, s)
            elif msg_type == STATUS_CODES.UPDATE.value and msg_context == UPD_CONTEXTS.END_OF_GAME.value:
                outcome = server_message["payload"][0]

                if outcome != OUTCOMES.WIN.value:
                    game_data.update_board(server_message["payload"][1], game_data.get_adversary())
                    game_data.print_board()

                print("You", EOF_MESSAGES[outcome], ". Opponent played", adversarys_play)
                exit(0)
            else:
                print("Unexpected message received from server")
                print(server_message)


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


def create_arguments() -> argparse:
    parser = argparse.ArgumentParser()

    parser.add_argument("host", help="server IP address")
    parser.add_argument("--port", help="server port #. Default = " + str(DEFAULT_PORT))

    return parser


def main():
    args = create_arguments().parse_args()

    try:
        port = int(args.port)
    except TypeError:
        port = DEFAULT_PORT

    play_game(args.host, port)


if __name__ == "__main__":
    main()
