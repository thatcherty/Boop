import sys
class trie:
    def __init__(self):
        self.three_in_a_row: dict[int, dict] = {}

    def pack_move(self, move):
        return (move[1] * 6) + move[0]
    
    def unpack_move(self, num):
        y = num // 6
        x = num % 6
        return x, y

    def add_seq(self, moves):
        level = self.three_in_a_row

        for move in range(len(moves) % 2, len(moves), 2):
            # may remove this if we create a hash elsewhere
            square = self.pack_move(moves[move])
            level = level.setdefault(square, {})
        level[-1] = True # this is the leaf node


if __name__ == "__main__":

    test1 = [[3, 2], [5, 1], [1, 0], [4, 4], [2, 5]]
    test2 = [[0, 3], [3, 3], [1, 2], [5, 5], [4, 1], [2, 2]]
    test3 = [[5, 0], [2, 3], [4, 2], [0, 1], [3, 4], [1, 0], [0, 0]]
    test4 = [[1, 4], [2, 5], [0, 2], [4, 3], [3, 1]]
    test5 = [[5, 5], [2, 1], [3, 0], [0, 5], [1, 3], [4, 4], [2, 2], [3, 3], [0, 0]]
    test6 = [[1, 4], [2, 5], [0, 2], [4, 3], [3, 2]]

    test = trie()

    # size of dictionary without any items is 64 bytes
    print(sys.getsizeof(test.three_in_a_row))

    test.add_seq(test1)
    test.add_seq(test2)
    test.add_seq(test3)
    test.add_seq(test4)
    test.add_seq(test5)
    test.add_seq(test6)

    # size of dictionary with 4 levels is 224 bytes
    # still 224 bytes with 9 levels
    print(sys.getsizeof(test.three_in_a_row))
