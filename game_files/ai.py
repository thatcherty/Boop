# This class contains the AI algorithms. It uses minimax and a heuristic.  Your primary task
# is to implement a better heuristic to improve the AI game play.

import random
import copy
from pieces import Piece, PieceType, PieceColor, GameState
from constants import BOARD_SIZE # We will need BOARD_SIZE from constants
from data_processing import *

class BoopAI:
    def __init__(self, game_instance, depth):
        self.game = game_instance # Reference to the main game object for rule checks
        self.depth = depth
        self.heuristic_trie = prepare_trie(True) # loads sequence data into trie for use
        self.current_node = self.heuristic_trie.root

    # Get all possible moves for the current player
    def get_possible_moves(self, player_idx, board, orange_cats, black_cats):
        moves = []

        # Get available piece types
        available_types = [PieceType.KITTEN]  # Always have kittens
        if (player_idx == 0 and orange_cats > 0) or \
           (player_idx == 1 and black_cats > 0):
            available_types.append(PieceType.CAT)

        # Check each empty position
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                if board[y][x] is None:
                    for piece_type in available_types:
                        moves.append((x, y, piece_type))
        return moves

    # Heuristic to evaluate the board state where bigger = better for orange, smaller (negative) = better for black
    def eval_board(self, board, orange_cats, black_cats):
        # Check for immediate win
        if self.game.player_won(0, board, orange_cats, black_cats):
            return 10000
        if self.game.player_won(1, board, orange_cats, black_cats):
            return -10000

        on_board_orange_cats = 0
        orange_kittens = 0
        on_board_black_cats = 0
        black_kittens = 0

        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                piece = board[y][x]
                if piece is not None:
                    if piece.color == PieceColor.ORANGE:
                        if piece.type == PieceType.CAT:
                            on_board_orange_cats += 1
                        else:
                            orange_kittens += 1
                    else:
                        if piece.type == PieceType.CAT:
                            on_board_black_cats += 1
                        else:
                            black_kittens += 1

        score = (4 * on_board_orange_cats + 2 * orange_cats + orange_kittens) - \
                (4 * on_board_black_cats + 2 * black_cats + black_kittens)
        
        score += (5 * orange_cats)
        score -= (5 * black_cats)

        return score
    
    # Minimax with alpha-beta pruning
    def minimax(self, board, orange_cats, black_cats, depth, alpha, beta, maximizing_player, current_player_idx):
        # Check for terminal states
        if self.game.player_won(1, board, orange_cats, black_cats):  # Black wins
            return -10000 - depth
        if self.game.player_won(0, board, orange_cats, black_cats):  # Orange wins
            return 10000 + depth

        if depth == 0:
            return self.eval_board(board, orange_cats, black_cats)

        moves = self.get_possible_moves(current_player_idx, board, orange_cats, black_cats)

        if not moves: # No possible moves, evaluate current board
            return self.eval_board(board, orange_cats, black_cats)

        if maximizing_player: # Orange (Player 0) is maximizing
            max_eval = float('-inf')
            for move in moves:

                x, y, piece_type = move

                # Make the move on a copy
                new_board = [row[:] for row in board]
                new_orange_cats = orange_cats
                new_black_cats = black_cats

                new_board[y][x] = Piece(piece_type, PieceColor.ORANGE) # Assuming current_player_idx is 0
                if piece_type == PieceType.CAT:
                    new_orange_cats -= 1

                # Apply booping
                # We need to make sure check_boop doesn't modify the main game board but the new_board
                self.game.check_boop(x, y, new_board)

                # Check for three in a row
                three_result = self.game.first_three_in_row(current_player_idx, new_board)
                if three_result['found']:
                    for px, py in three_result['positions']:
                        new_board[py][px] = None
                    new_orange_cats += 3

                # Recursive call for the next player (minimizing player)
                eval_score = self.minimax(new_board, new_orange_cats, new_black_cats,
                                        depth - 1, alpha, beta, False, 1 - current_player_idx)

                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)

                if beta <= alpha:
                    break  # Alpha-beta pruning
            return max_eval
        else: # Black (Player 1) is minimizing
            min_eval = float('inf')
            for move in moves:
                x, y, piece_type = move

                # Make the move on a copy
                new_board = [row[:] for row in board]
                new_orange_cats = orange_cats
                new_black_cats = black_cats

                new_board[y][x] = Piece(piece_type, PieceColor.BLACK) # Assuming current_player_idx is 1
                if piece_type == PieceType.CAT:
                    new_black_cats -= 1

                # Apply booping
                self.game.check_boop(x, y, new_board)

                # Check for three in a row
                three_result = self.game.first_three_in_row(current_player_idx, new_board)
                if three_result['found']:
                    for px, py in three_result['positions']:
                        new_board[py][px] = None
                    new_black_cats += 3

                # Recursive call for the next player (maximizing player)
                eval_score = self.minimax(new_board, new_orange_cats, new_black_cats,
                                        depth - 1, alpha, beta, True, 1 - current_player_idx)

                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)

                if beta <= alpha:
                    break  # Alpha-beta pruning
            return min_eval

    # Get the best move for AI
    def get_best_move(self, board, orange_cats, black_cats, current_player_idx, sequence: str):
        best_move = None

        moves = self.get_possible_moves(current_player_idx, board, orange_cats, black_cats)

        """
        This is the section that defines the agents use of the trie instead of a function to find a heuristic value for possible moves
        We are having the orange player use the trie and leaving the existing method for the black player
        """
        if current_player_idx == 0: # Orange is making a move, try to use the trie heuristic
            current_node = self.heuristic_trie.root
            trie_nodes = current_node.children
            for move in sequence:
                if move in current_node.children:
                    current_node = current_node.children[move]
                    trie_nodes = current_node.children
                else:
                    trie_nodes = {}
                    print("--" * 10)
                    print("Game sequence is no longer contained in collected game trie")
                    print("Defaulting to existing heuristic")
                    print("--" * 10)
            if trie_nodes: # if trie_nodes is empty then default to existing heuristic function 
                best_board_move = ()
                high_score = float('-inf')
                for move, node in trie_nodes.items():
                    
                    # check that the move is available
                    poss_move = decode_position(move) + (PieceType.KITTEN,)

                    if poss_move not in moves:
                        continue     

                    if node.heuristic_value > high_score:
                        high_score = node.heuristic_value
                        best_board_move = decode_position(move)
                print("\n", "Trie Heuristic score:", high_score)
                best_trie_move = best_board_move + (PieceType.KITTEN,) # building a tuple in required format

                # in case none of the moves were available
                if best_trie_move:
                    return best_trie_move
                

        # Shuffle moves to add variety, especially helpful if multiple moves have the same score
        random.shuffle(moves)

        # Determine if AI is maximizing or minimizing based on whose turn it is
        maximizing_player = (current_player_idx == 0) # Orange is maximizing, Black is minimizing

        if maximizing_player:
            best_score = float('-inf')
        else:
            best_score = float('inf')

        for move in moves:
            x, y, piece_type = move

            # Make the move on a copy
            new_board = [row[:] for row in board]
            new_orange_cats = orange_cats
            new_black_cats = black_cats

            my_color = PieceColor.ORANGE if current_player_idx == 0 else PieceColor.BLACK
            new_board[y][x] = Piece(piece_type, my_color)

            if piece_type == PieceType.CAT:
                if current_player_idx == 0:
                    new_orange_cats -= 1
                else:
                    new_black_cats -= 1

            # Apply booping
            self.game.check_boop(x, y, new_board)

            # Check for three in a row
            three_result = self.game.first_three_in_row(current_player_idx, new_board)
            if three_result['found']:
                for px, py in three_result['positions']:
                    new_board[py][px] = None
                if current_player_idx == 0:
                    new_orange_cats += 3
                else:
                    new_black_cats += 3
            
            # Evaluate this move (recursive call for the opponent)
            # If current_player_idx is 0 (Orange, maximizing), the next player is 1 (Black, minimizing).
            # So, for the recursive call, the maximizing_player flag should be False.
            # If current_player_idx is 1 (Black, minimizing), the next player is 0 (Orange, maximizing).
            # So, for the recursive call, the maximizing_player flag should be True.
            score = self.minimax(new_board, new_orange_cats, new_black_cats,
                                 self.depth - 1, float('-inf'), float('inf'),
                                 not maximizing_player, 1 - current_player_idx)

            if maximizing_player:
                if score > best_score:
                    best_score = score
                    best_move = move
            else: # Minimizing player
                if score < best_score:
                    best_score = score
                    best_move = move
        
        print("\n", "default heuristic function score:", best_score)
        return best_move