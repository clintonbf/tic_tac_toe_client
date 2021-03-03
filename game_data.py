import socket

class GameData:

    def __init__(self):
        self.__identity = None
        self.__game_board = [45, 45, 45, 45, 45, 45, 45, 45, 45]
        self.__bytes_to_expect = 1
        self.__version = 1

    def get_identity(self):
        return self.__identity

    def get_game_board(self):
        return self.__game_board

    def get_bytes_to_expect(self):
        return self.__bytes_to_expect

    def set_identity(self, identity):
        self.__identity = identity

    def set_game_board(self, board):
        self.__game_board = board

    def set_bytes_to_expect(self, bytes_to_expect):
        self.__bytes_to_expect = bytes_to_expect

    def set_play(self, position):
        self.__game_board[position] = self.__identity

    def print_board(self):
        """
        Prints the board in a formatted way.

        :param board: the board. Values are ints.
        :return:  void
        """

        print("Board update:")

        count = 0

        for c in self.__game_board:
            i = int(c)

            print(chr(i), end='')

            self.printSeparator(count)

            count += 1

    def printSeparator(self, count: int):
        """
        Prints out formatted characters for the board.

        :param count: int
        :return: void
        """
        if count == 0 or count == 3 or count == 6:
            print("|", end='')
            return

        if count == 1 or count == 4 or count == 7:
            print("|", end='')
            return

        if count == 2 or count == 5:
            print("\n-+-+-")
            return

        if count == 8:
            print('')
            return

    def make_play(self, s: socket, invitation: str):
        proposed_play = input(invitation)

        play_ord = ord(proposed_play)
        s.sendall(play_ord.to_bytes(1, 'big'))

        return int(proposed_play)

    def get_version(self):
        print("Protocol version", self.__version)

    def process_welcome(self, s: socket, message: str):
        print(message)

        self.set_identity(int.from_bytes(s.recv(self.get_bytes_to_expect()), 'big'))
        print("You are player", chr(self.get_identity()))


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

    def process_welcome(self, s: socket, message: str):
        super().process_welcome(s, message)
        self.get_game_id(int.from_bytes(s.recv(self.get_bytes_to_expect()), 'big'))
