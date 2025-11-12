import numpy as np

class Sequence_library:
    def __init__(self):
        self.sequences_dict = {}

    def add_sequence(self, sequence_list, count):
        self.sequences_dict[count] = sequence_list 

        
class Sequence:
    def __init__(self):
        self.moves = []
        self.num_of_plays = 0
        self.winner = ""

    def add_move(self, x, y, age, player):
        self.moves.append([x, y, age])
        self.num_of_plays += 1
        if player == 0:
            self.winner = "orange"
        else:
            self.winner = "black"

    def print_data (self):
        print(f"total number of moves to trio: ", self.num_of_plays)
        print(f"color of trio: ", self.winner)