import pygame
import sys
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, BOARD_SIZE, CELL_SIZE, BOARD_START_X, BOARD_START_Y,
    WHITE, BLACK, GRAY, LIGHT_BLUE, ORANGE, NAVY, BLUE,
    KITTEN_O_SPRITE, CAT_O_SPRITE, KITTEN_B_SPRITE, CAT_B_SPRITE
)
from pieces import PieceType, PieceColor, PlayerType
from game import BoopGame

class GameGUI:
    def __init__(self, game_instance):
        pygame.init()
        self.game = game_instance
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Boop - Board Game")
        self.clock = pygame.time.Clock()

        # Fonts
        self.font = pygame.font.Font(None, 32)
        self.large_font = pygame.font.Font(None, 46)

        # Load sprites
        self.kitten_o_sprite = self._load_sprite(KITTEN_O_SPRITE, ORANGE)
        self.cat_o_sprite = self._load_sprite(CAT_O_SPRITE, (255, 100, 0)) # Darker orange
        self.kitten_b_sprite = self._load_sprite(KITTEN_B_SPRITE, BLACK)
        self.cat_b_sprite = self._load_sprite(CAT_B_SPRITE, (64, 64, 64)) # Dark gray

        self.ai_thinking = False # Flag for GUI to show AI thinking message

    def _load_sprite(self, path, fallback_color):
        try:
            sprite = pygame.image.load(path).convert_alpha()
            print(f"Loaded {path}")
            return sprite
        except pygame.error as e:
            print(f"Could not load sprite {path}: {e}. Using fallback rectangle.")
            fallback_sprite = pygame.Surface((80, 80))
            fallback_sprite.fill(fallback_color)
            return fallback_sprite

    # Convert mouse position to board coordinate if we clicked on a board location
    def mouse_to_board_pos(self, mouse_x, mouse_y):
        board_x = (mouse_x - BOARD_START_X) // CELL_SIZE
        board_y = (mouse_y - BOARD_START_Y) // CELL_SIZE

        if 0 <= board_x < BOARD_SIZE and 0 <= board_y < BOARD_SIZE:
            return board_x, board_y
        return None, None

    # Draws the main game board with the pieces
    def draw_board(self):
        # Draw board background
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                rect = pygame.Rect(
                    BOARD_START_X + x * CELL_SIZE,
                    BOARD_START_Y + y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                pygame.draw.rect(self.screen, LIGHT_BLUE, rect)
                pygame.draw.rect(self.screen, BLACK, rect, 2)

        # Draw pieces
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                piece = self.game.board[y][x]
                center_x = BOARD_START_X + x * CELL_SIZE + CELL_SIZE // 2
                center_y = BOARD_START_Y + y * CELL_SIZE + CELL_SIZE // 2
                if piece is not None:
                    if piece.color == PieceColor.ORANGE:
                        if piece.type == PieceType.KITTEN:
                            sprite_rect = self.kitten_o_sprite.get_rect(center=(center_x, center_y))
                            self.screen.blit(self.kitten_o_sprite, sprite_rect)
                        elif piece.type == PieceType.CAT:
                            sprite_rect = self.cat_o_sprite.get_rect(center=(center_x, center_y))
                            self.screen.blit(self.cat_o_sprite, sprite_rect)
                    else: # Black
                        if piece.type == PieceType.KITTEN:
                            sprite_rect = self.kitten_b_sprite.get_rect(center=(center_x, center_y))
                            self.screen.blit(self.kitten_b_sprite, sprite_rect)
                        elif piece.type == PieceType.CAT:
                            sprite_rect = self.cat_b_sprite.get_rect(center=(center_x, center_y))
                            self.screen.blit(self.cat_b_sprite, sprite_rect)
                if (x == self.game.last_placed_pos[0] and y == self.game.last_placed_pos[1]):
                    outline_rect = self.cat_o_sprite.get_rect(center=(center_x, center_y)) # Use a generic rect size
                    pygame.draw.rect(self.screen, WHITE, outline_rect, width=2)


    # Draws coordinate labels
    def draw_labels(self):
        # X-axis labels (0-5)
        for x in range(BOARD_SIZE):
            label_x = BOARD_START_X + x * CELL_SIZE + CELL_SIZE // 2
            label_y = BOARD_START_Y - 25

            text = self.font.render(str(x), True, WHITE)
            text_rect = text.get_rect(center=(label_x, label_y))

            # Background
            bg_rect = text_rect.inflate(10, 6)
            pygame.draw.rect(self.screen, BLACK, bg_rect)
            self.screen.blit(text, text_rect)

        # Y-axis labels (0-5)
        for y in range(BOARD_SIZE):
            label_x = BOARD_START_X - 25
            label_y = BOARD_START_Y + y * CELL_SIZE + CELL_SIZE // 2

            text = self.font.render(str(y), True, WHITE)
            text_rect = text.get_rect(center=(label_x, label_y))

            # Background
            bg_rect = text_rect.inflate(10, 6)
            pygame.draw.rect(self.screen, BLACK, bg_rect)
            self.screen.blit(text, text_rect)

    # Draw the GUI including number of cats, whose turn it is
    def draw_ui(self):
        # Title
        game_title = f"boop."
        text = self.large_font.render(game_title, True, BLUE)
        self.screen.blit(text, (620,20))

        # Game Over
        if self.game.win_msg != "":
            text = self.large_font.render(self.game.win_msg, True, BLUE)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 750))
            self.screen.blit(text, text_rect)
            return # Don't draw turn info if game is over

        # Orange player UI
        if (self.game.whoseturn == 0):
            pygame.draw.rect(self.screen, NAVY, (25,125,280,100))
            if self.ai_thinking and self.game.player0 == PlayerType.AI:
                turn_text = f"AI thinking..."
                text = self.large_font.render(turn_text, True, ORANGE)
                self.screen.blit(text, (50, 150))
            else:
                turn_text = f"Orange's turn!"
                text = self.large_font.render(turn_text, True, ORANGE)
                self.screen.blit(text, (50, 150))
        else:
            turn_text = f"Orange"
            text = self.large_font.render(turn_text, True, ORANGE)
            self.screen.blit(text, (50, 150))

        # Black player UI
        if (self.game.whoseturn == 1):
            pygame.draw.rect(self.screen, NAVY, (1025,125,280,100)) # Changed to NAVY for consistency
            if self.ai_thinking and self.game.player1 == PlayerType.AI:
                turn_text = f"AI thinking..."
                text = self.large_font.render(turn_text, True, BLACK)
                self.screen.blit(text, (1050, 150))
            else:
                turn_text = f"Black's turn!"
                text = self.large_font.render(turn_text, True, BLACK)
                self.screen.blit(text, (1050, 150))
        else:
            turn_text = f"Black"
            text = self.large_font.render(turn_text, True, BLACK)
            self.screen.blit(text, (1050, 150))

        # Cats and kittens counts for Orange
        text = self.font.render("cats: " + str(self.game.orange_cats), True, ORANGE)
        self.screen.blit(text, (30, 450))
        text = self.font.render("kittens: inf", True, ORANGE)
        self.screen.blit(text, (30, 680))

        # Orange piece selection sprites
        grayed_cat_o = self.cat_o_sprite.copy()
        grayed_cat_o.set_alpha(100) # Slightly more opaque
        grayed_kitten_o = self.kitten_o_sprite.copy()
        grayed_kitten_o.set_alpha(100)

        if self.game.whoseturn == 0 and self.game.player0 == PlayerType.HUMAN:
            if self.game.orange_cats > 0:
                self.screen.blit(self.cat_o_sprite, (30, 480))
            else:
                self.screen.blit(grayed_cat_o, (30, 480))
            self.screen.blit(self.kitten_o_sprite, (30, 580))
        else: # Not Orange's human turn
            self.screen.blit(grayed_cat_o, (30, 480))
            self.screen.blit(grayed_kitten_o, (30, 580))


        # Cats and kittens counts for Black
        text = self.font.render("cats: " + str(self.game.black_cats), True, BLACK)
        self.screen.blit(text, (1050, 450))
        text = self.font.render("kittens: inf", True, BLACK)
        self.screen.blit(text, (1050, 680))

        # Black piece selection sprites
        grayed_cat_b = self.cat_b_sprite.copy()
        grayed_cat_b.set_alpha(100)
        grayed_kitten_b = self.kitten_b_sprite.copy()
        grayed_kitten_b.set_alpha(100)

        if self.game.whoseturn == 1 and self.game.player1 == PlayerType.HUMAN:
            if self.game.black_cats > 0:
                self.screen.blit(self.cat_b_sprite, (1050, 480))
            else:
                self.screen.blit(grayed_cat_b, (1050, 480))
            self.screen.blit(self.kitten_b_sprite, (1050, 580))
        else: # Not Black's human turn
            self.screen.blit(grayed_cat_b, (1050, 480))
            self.screen.blit(grayed_kitten_b, (1050, 580))

        # Change cursor to hand if over cat or kitten (only for human player)
        ocat_rect = pygame.Rect(30, 480, 96, 96)
        okitten_rect = pygame.Rect(30, 580, 96, 96)
        bcat_rect = pygame.Rect(1050, 480, 96, 96)
        bkitten_rect = pygame.Rect(1050, 580, 96, 96)

        current_player_type = self.game.player0 if self.game.whoseturn == 0 else self.game.player1

        if current_player_type == PlayerType.HUMAN:
            mouse_pos = pygame.mouse.get_pos()
            if self.game.whoseturn == 0: # Orange human
                if ocat_rect.collidepoint(mouse_pos) and self.game.orange_cats > 0:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                elif okitten_rect.collidepoint(mouse_pos):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                else:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            else: # Black human
                if bcat_rect.collidepoint(mouse_pos) and self.game.black_cats > 0:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                elif bkitten_rect.collidepoint(mouse_pos):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                else:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW) # AI is playing, no hand cursor

        # Box around selected piece type
        if self.game.whoseturn == 0:
            if self.game.orange_last_selection == PieceType.KITTEN:
                pygame.draw.rect(self.screen, BLUE, okitten_rect, width=2)
            else:
                pygame.draw.rect(self.screen, BLUE, ocat_rect, width=2)
        else: # Black's turn
            if self.game.black_last_selection == PieceType.KITTEN:
                pygame.draw.rect(self.screen, BLUE, bkitten_rect, width=2)
            else:
                pygame.draw.rect(self.screen, BLUE, bcat_rect, width=2)

    # Handles clicking on a place on the board or one of the pieces to place
    def handle_click(self, mouse_x, mouse_y):
        # Only allow human moves when it's their turn and game is not over
        if self.game.win_msg != "":
            return

        current_player_idx = self.game.whoseturn
        current_player_type = self.game.player0 if current_player_idx == 0 else self.game.player1

        if current_player_type == PlayerType.AI:
            return # AI handles its own moves

        # Handle piece selection clicks for human player
        ocat_rect = pygame.Rect(30, 480, 96, 96)
        okitten_rect = pygame.Rect(30, 580, 96, 96)
        bcat_rect = pygame.Rect(1050, 480, 96, 96)
        bkitten_rect = pygame.Rect(1050, 580, 96, 96)

        if current_player_idx == 0: # Orange
            if ocat_rect.collidepoint(mouse_x, mouse_y):
                if self.game.orange_cats > 0:
                    self.game.orange_last_selection = PieceType.CAT
                    print("Orange selected CAT")
                    return # Handled selection, not a board placement
            elif okitten_rect.collidepoint(mouse_x, mouse_y):
                self.game.orange_last_selection = PieceType.KITTEN
                print("Orange selected KITTEN")
                return # Handled selection, not a board placement
        else: # Black
            if bcat_rect.collidepoint(mouse_x, mouse_y):
                if self.game.black_cats > 0:
                    self.game.black_last_selection = PieceType.CAT
                    print("Black selected CAT")
                    return # Handled selection, not a board placement
            elif bkitten_rect.collidepoint(mouse_x, mouse_y):
                self.game.black_last_selection = PieceType.KITTEN
                print("Black selected KITTEN")
                return # Handled selection, not a board placement

        # Handle click on the board
        board_x, board_y = self.mouse_to_board_pos(mouse_x, mouse_y)

        if board_x is not None and self.game.is_empty(board_x, board_y):
            # Get the currently selected piece type for the current player
            piece_to_place = None
            if current_player_idx == 0:
                piece_to_place = self.game.orange_last_selection
            else:
                piece_to_place = self.game.black_last_selection

            # Attempt to process the move through the game logic
            self.game.process_move(board_x, board_y, piece_to_place)

    # Draw the game board and UI
    def draw(self):
        self.screen.fill(GRAY)
        self.draw_board()
        self.draw_labels()
        self.draw_ui()
        pygame.display.flip()

    # Handle Pygame events
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.handle_click(event.pos[0], event.pos[1])

    def update_ai_thinking_status(self, thinking_status):
        self.ai_thinking = thinking_status