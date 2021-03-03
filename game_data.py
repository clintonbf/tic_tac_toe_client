class GameData:

    def __init__(self):
        self.__identity = None
        self.__game_board = [45, 45, 45, 45, 45, 45, 45, 45, 45]
        self.__bytes_to_expect = 1
        self.__game_id = None

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
        self.__game_board[position] = chr(self.__identity)

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

        