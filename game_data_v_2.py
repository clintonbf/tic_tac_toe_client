import socket
from game_data import GameData

class GameData_v2(GameData):
    def __init__(self):
        super().__init__()
        self.__game_id = None
        self.__version = 2

    def get_game_id(self):
        return self.__game_id

    def set_game_id(self, id):
        self.__game_id = id

    def make_play(self, s: socket, invitation: str):
        proposed_play = input(invitation)

        play_ord = ord(proposed_play)
        s.sendall(self.__game_id.to_bytes(1, 'big'))
        s.sendall(play_ord.to_bytes(1, 'big'))

        return int(proposed_play)