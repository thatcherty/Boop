# This class implements game logic to determine legal moves, if someone has won, play sounds, etc.

import pygame
import copy
from pieces import Piece, PieceType, PieceColor, PlayerType
from constants import BOARD_SIZE, KITTEN_MEOW_SOUND, CAT_MEOW_SOUND, BOOP_SOUND, CHEER_SOUND
from ai import BoopAI
from data_processing import encode_position, Trie, prepare_trie, append_output_file

# Main game class
class BoopGame:
    def __init__(self, ai_depth=1):
        # Game state and key game variables
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.whoseturn = 0  # 0 = orange (player0), 1 = black (player1)
        self.orange_cats = 0
        self.black_cats = 0
        self.win_msg = ""
        self.last_placed_pos = (-1,-1)
        self.orange_last_selection = PieceType.KITTEN
        self.black_last_selection = PieceType.KITTEN
        self.player0 = PlayerType.AI  # CHANGE FOR AI or HUMAN
        self.player1 = PlayerType.AI  # CHANGE FOR AI or HUMAN
        self.sequence = ""
        self.game_trie = prepare_trie()
        self.current_node = self.game_trie.root
        self.follow_trie = False
        self.sequence_found = False

        

        self.ai = BoopAI(self, ai_depth) # Pass self to AI for rule checks

        # Sounds (will be loaded by the GUI, but we can have dummy placeholders)
        self.kitten_meow = None
        self.cat_meow = None
        self.boop = None
        self.cheer = None
        if not pygame.mixer.get_init(): 
            pygame.mixer.init()
        #self._load_sounds() # Load sounds directly here

    def _load_sounds(self):
        try:
            self.kitten_meow = pygame.mixer.Sound(KITTEN_MEOW_SOUND)
            self.cat_meow = pygame.mixer.Sound(CAT_MEOW_SOUND)
            self.boop = pygame.mixer.Sound(BOOP_SOUND)
            self.cheer = pygame.mixer.Sound(CHEER_SOUND)
        except pygame.error as e:
            print(f"Could not load sound files: {e}. Sounds will not play.")
            # Create dummy sounds if files don't exist
            self.kitten_meow = None
            self.cat_meow = None
            self.boop = None
            self.cheer = None


    # True if a cell is empty
    def is_empty(self, x, y, board=None):
        if board is None:
            board = self.board
        return board[y][x] is None

    # Places a piece on the board
    def place_piece(self, x, y, piece, board=None):
        if board is None:
            board = self.board
        if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
            board[y][x] = piece
            self.last_placed_pos = (x,y)
            #print(f"{piece.color} {piece.type} placed at {x},{y}")
            return True
        return False

    # Check if position is within the board dimensions
    def is_valid_position(self, x, y):
        return (0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE)

    # Check in all directions for booping
    def check_boop(self, placed_x, placed_y, board=None):
        playSound = False
        if board is None:
            board = self.board
        #    playSound = True

        moves_made = []

        # Determine if we placed a cat or a kitten
        if board[placed_y][placed_x] is None: # Should not happen, but for safety
            return moves_made

        is_placed_piece_cat = (board[placed_y][placed_x].type == PieceType.CAT)

        # Check in all 8 directions
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue

                target_x = placed_x + dx
                target_y = placed_y + dy

                # If there's a piece adjacent to our placed piece
                if (self.is_valid_position(target_x, target_y)) and board[target_y][target_x] is not None:
                    target_piece = board[target_y][target_x]
                    is_target_piece_cat = (target_piece.type == PieceType.CAT)

                    # If the placed piece is a kitten, it cannot boop cats
                    if not is_placed_piece_cat and is_target_piece_cat:
                        continue

                    # Calculate where it would be pushed to
                    push_to_x = target_x + dx
                    push_to_y = target_y + dy

                    # Check if push destination is valid and empty
                    if (self.is_valid_position(push_to_x, push_to_y)) and board[push_to_y][push_to_x] is None:
                        # Do boop
                        board[push_to_y][push_to_x] = target_piece
                        board[target_y][target_x] = None
                        moves_made.append({
                            'from': (target_x, target_y),
                            'to': (push_to_x, push_to_y),
                            'piece': target_piece
                        })
                        if self.boop and playSound: self.boop.play()
                    elif not self.is_valid_position(push_to_x, push_to_y):
                        # Boop off board
                        board[target_y][target_x] = None
                        moves_made.append({
                            'from': (target_x, target_y),
                            'to': (-1, -1), # Indicates off board
                            'piece': target_piece
                        })
                        if self.boop and playSound: self.boop.play()
        return moves_made

    # Helper function that determines if the specified player owns the specified piece
    def owns_piece(self, piece, player_idx):
        if player_idx == 0: # Orange
            return (piece.color == PieceColor.ORANGE)
        else: # Black
            return (piece.color == PieceColor.BLACK)

    # Finds if there are three in a row with at least one kitten for the specified player
    def first_three_in_row(self, player_idx, board=None):
        if board is None:
            board = self.board

        directions = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,-1),(-1,1)]
        # Store all valid three-in-a-row formations with at least one kitten
        valid_trios = []

        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                piece1 = board[y][x]
                if piece1 is None or not self.owns_piece(piece1, player_idx):
                    continue

                for dx, dy in directions:
                    pos1_x, pos1_y = x + dx, y + dy
                    pos2_x, pos2_y = x + dx * 2, y + dy * 2

                    if not (self.is_valid_position(pos1_x, pos1_y) and self.is_valid_position(pos2_x, pos2_y)):
                        continue

                    piece2 = board[pos1_y][pos1_x]
                    piece3 = board[pos2_y][pos2_x]

                    if piece2 is None or piece3 is None:
                        continue
                    if not (self.owns_piece(piece2, player_idx) and self.owns_piece(piece3, player_idx)):
                        continue

                    found_kitten = (piece1.type == PieceType.KITTEN or
                                    piece2.type == PieceType.KITTEN or
                                    piece3.type == PieceType.KITTEN)

                    if found_kitten:
                        # Ensure we don't add duplicate trios (e.g., (0,0)-(0,1)-(0,2) and (0,2)-(0,1)-(0,0))
                        # By sorting the positions and adding them as a tuple of tuples.
                        current_trio_positions = tuple(sorted([(x, y), (pos1_x, pos1_y), (pos2_x, pos2_y)]))
                        if current_trio_positions not in [tuple(sorted(t['positions'])) for t in valid_trios]:
                             valid_trios.append({
                                'found': True,
                                'piece_type': piece1.type, # This doesn't matter much for resolution
                                'positions': [(x, y), (pos1_x, pos1_y), (pos2_x, pos2_y)]
                            })
        
        # As per the modified rules, if multiple trios exist, choose the one with smallest y, then smallest x
        if valid_trios:
            # Sort valid trios by the smallest (y, x) coordinate of the first piece in the trio
            # This logic needs to be careful: the rule states "the trio that contains the piece with the smallest y coordinate
            # followed by the smallest x coordinate". This applies to ANY piece in the trio, not just the "first" one we found.
            def get_min_coords_for_trio(trio_info):
                min_y = float('inf')
                min_x = float('inf')
                for px, py in trio_info['positions']:
                    if py < min_y:
                        min_y = py
                        min_x = px
                    elif py == min_y and px < min_x:
                        min_x = px
                return (min_y, min_x)

            valid_trios.sort(key=get_min_coords_for_trio)
            return valid_trios[0] # Return the chosen trio
        
        return {'found': False}

    # Returns true if the specified player has won
    def player_won(self, player_idx, board=None, orange_cats=None, black_cats=None):
        if board is None:
            board = self.board
        if orange_cats is None:
            orange_cats = self.orange_cats
        if black_cats is None:
            black_cats = self.black_cats

        # Check if 8+ cats on the board
        count_cats_on_board = 0
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                if board[y][x] is not None and \
                   self.owns_piece(board[y][x], player_idx) and \
                   board[y][x].type == PieceType.CAT:
                    count_cats_on_board += 1

        if count_cats_on_board >= 8:
            return True

        # Check 3 cats in a row (no kittens allowed)
        directions = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,-1),(-1,1)]
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                piece1 = board[y][x]
                if piece1 is None or not self.owns_piece(piece1, player_idx) or piece1.type == PieceType.KITTEN:
                    continue

                # Check each direction
                for dx, dy in directions:
                    pos1_x, pos1_y = x + dx, y + dy
                    pos2_x, pos2_y = x + dx * 2, y + dy * 2

                    if not (self.is_valid_position(pos1_x, pos1_y) and self.is_valid_position(pos2_x, pos2_y)):
                        continue

                    piece2 = board[pos1_y][pos1_x]
                    piece3 = board[pos2_y][pos2_x]

                    if piece2 is None or piece3 is None:
                        continue
                    if not (self.owns_piece(piece2, player_idx) and self.owns_piece(piece3, player_idx)):
                        continue
                    if (piece2.type == PieceType.KITTEN or piece3.type == PieceType.KITTEN):
                        continue # All three must be cats

                    return True # Found 3 cats in a row
        return False

    # Process a player's move (human or AI)
    # Returns True if a move was successfully processed and the turn ended, False otherwise
    def process_move(self, x, y, piece_type, sampling):
        current_player_idx = self.whoseturn
        player_color = PieceColor.ORANGE if current_player_idx == 0 else PieceColor.BLACK

        if not self.is_empty(x, y):
            print("Cannot place on occupied cell.")
            return False # Invalid move

        # Place piece
        self.place_piece(x, y, Piece(piece_type, player_color))

        # Encode move
        pos = encode_position(x, y)
        
        print(pos)

        # if value in Trie, advance
        child = self.current_node.get_child(pos)
        if child is not None:
            self.current_node = child
            self.follow_trie = True
        else:
            self.current_node = self.game_trie.root
            self.follow_trie = False

        # Add Move to queue
        self.sequence += pos

        # Update cats count if a cat was placed
        if piece_type == PieceType.CAT:
            if current_player_idx == 0:
                self.orange_cats -= 1
                if self.orange_cats == 0:
                    self.orange_last_selection = PieceType.KITTEN
            else:
                self.black_cats -= 1
                if self.black_cats == 0:
                    self.black_last_selection = PieceType.KITTEN

        # # Play sound for placement
        # if piece_type == PieceType.KITTEN and self.kitten_meow:
        #     self.kitten_meow.play()
        # elif piece_type == PieceType.CAT and self.cat_meow:
        #     self.cat_meow.play()

        # Check for boop
        boop_results = self.check_boop(x, y)
        if boop_results and self.boop: # boop sound is played within check_boop now
            pass

        # Check for three in a row
        three_result = self.first_three_in_row(current_player_idx)
        if three_result['found']:
            
            # playing until 3 in a row
            if (sampling):
                print(self.sequence)
                print(f"number of moves until trio: ", len(self.sequence))
                append_output_file(self.sequence)

                if current_player_idx == 0:
                    self.orange_cats += 3
                    self.win_msg = "Orange trio!"
                    print("Orange trio!")
                else:
                    self.black_cats += 3
                    self.win_msg = "Black trio!"
                    print("Black trio!")
            # playing game until win
            else:
                self.current_node = self.game_trie.root
                for px,py in three_result['positions']:
                    self.board[py][px] = None
                if current_player_idx == 0:
                    self.orange_cats += 3
                    print("Orange trio!")
                else:
                    self.black_cats += 3
                    print("Black trio!")


        # Check for win
        if self.player_won(current_player_idx):
            if self.cheer: self.cheer.play()
            if current_player_idx == 0:
                self.win_msg = "Orange Wins!"
            else:
                self.win_msg = "Black Wins!"

        # Switch players if no win
        if not self.win_msg:
            self.whoseturn = 0 if self.whoseturn == 1 else 1
        return True

    # Make AI move
    def make_ai_move(self, trie):
        current_player_idx = self.whoseturn
        # Ensure it's AI's turn
        if (current_player_idx == 0 and self.player0 == PlayerType.HUMAN) or \
           (current_player_idx == 1 and self.player1 == PlayerType.HUMAN) or \
           self.win_msg:
            return

        #print(f"AI {('Orange' if current_player_idx == 0 else 'Black')} is thinking...")
        best_move = self.ai.get_best_move(trie, self.board, self.current_node, self.orange_cats, self.black_cats, current_player_idx)
            

        if best_move:
            x, y, piece_type = best_move

            #print(f"AI chooses to place {piece_type.name} at ({x},{y})")
            self.process_move(x, y, piece_type, not trie)
        else:
            print("AI found no moves, this should not happen unless board is full or game ended.")