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

        for move in moves:
            # may remove this if we create a hash elsewhere
            square = self.pack_move(move)
            level = level.setdefault(square, {})
        level[-1] = True # this is the leaf node


if __name__ == "__main__":

    test_moves = [[5,6], [3,4], [7,8], [2,1]]

    test = trie()

    test.add_seq(test_moves)

