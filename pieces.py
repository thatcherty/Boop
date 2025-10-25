# This class has enumerations and information about managing pieces and a board

from enum import Enum

# Enumerations allow for more english-like programming
class PieceType(Enum):
    KITTEN = 0
    CAT = 1
    EMPTY = -1

class PieceColor(Enum):
    ORANGE = "orange"
    BLACK = "black"

class PlayerType(Enum):
    HUMAN = 0
    AI = 1

# Keep track of the color and type of a piece
class Piece:
    def __init__(self, type=PieceType.KITTEN, color=PieceColor.ORANGE):
        self.color = color
        self.type = type

    def __repr__(self):
        return f"Piece({self.color.name}, {self.type.name})"

    def __eq__(self, other):
        if not isinstance(other, Piece):
            return NotImplemented
        return self.color == other.color and self.type == other.type

    def __hash__(self):
        return hash((self.color, self.type))

# Represents the state of the game for AI evaluation
class GameState:
    def __init__(self, board, orange_cats, black_cats, current_player):
        self.board = [row[:] for row in board]  # Deep copy
        self.orange_cats = orange_cats
        self.black_cats = black_cats
        self.current_player = current_player

    def copy(self):
        return GameState(self.board, self.orange_cats, self.black_cats, self.current_player)

    def __repr__(self):
        board_str = "\n".join([" ".join([p.color.name[0] + p.type.name[0] if p else "--" for p in row]) for row in self.board])
        return (f"GameState(\nBoard:\n{board_str},\n"
                f"Orange Cats: {self.orange_cats}, Black Cats: {self.black_cats},\n"
                f"Current Player: {self.current_player})\n")