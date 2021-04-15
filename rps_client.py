import argparse
from struct import *
from game_data import *
from protocol import *

MAX_VERSION = 4
DEFAULT_PORT = 2034
GAME_ID = 2


def play_game(host: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        game_data = GameData_rps()

        game_data.set_uid(handshake(s, GAME_ID))
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
