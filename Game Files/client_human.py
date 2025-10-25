# This class implements the networking/logic portion of a human client.
# It pops up a GUI where the user can click on where to place a piece.
#
# Run with python client_human.py <host> <port>
# The default host is localhost and the port is 5555
#
import pygame
import socket
import json
import sys
import threading
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, BOARD_SIZE, CELL_SIZE, BOARD_START_X, BOARD_START_Y,
    WHITE, BLACK, GRAY, LIGHT_BLUE, ORANGE, NAVY, BLUE,
    KITTEN_O_SPRITE, CAT_O_SPRITE, KITTEN_B_SPRITE, CAT_B_SPRITE
)
from pieces import PieceType, PieceColor, Piece

class HumanClient:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.socket = None
        self.player_idx = None
        self.my_color = None
        
        # Game state
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.whoseturn = 0
        self.orange_cats = 0
        self.black_cats = 0
        self.win_msg = ""
        self.last_placed_pos = (-1, -1)
        self.selected_piece = PieceType.KITTEN
        
        # GUI
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Boop - Client")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.large_font = pygame.font.Font(None, 46)
        
        # Load sprites
        self.kitten_o_sprite = self._load_sprite(KITTEN_O_SPRITE, ORANGE)
        self.cat_o_sprite = self._load_sprite(CAT_O_SPRITE, (255, 100, 0))
        self.kitten_b_sprite = self._load_sprite(KITTEN_B_SPRITE, BLACK)
        self.cat_b_sprite = self._load_sprite(CAT_B_SPRITE, (64, 64, 64))
        
        self.running = True
        self.connected = False
        
    def _load_sprite(self, path, fallback_color):
        try:
            sprite = pygame.image.load(path).convert_alpha()
            return sprite
        except pygame.error as e:
            print(f"Could not load sprite {path}: {e}. Using fallback.")
            fallback_sprite = pygame.Surface((80, 80))
            fallback_sprite.fill(fallback_color)
            return fallback_sprite
    
    def connect(self):
        """Connect to the server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"Connected to server at {self.host}:{self.port}")
            self.connected = True
            
            # Start listening thread
            listen_thread = threading.Thread(target=self.listen_to_server)
            listen_thread.daemon = True
            listen_thread.start()
            
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False
    
    def listen_to_server(self):
        """Listen for messages from server"""
        buffer = ""
        while self.running and self.connected:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    print("Disconnected from server")
                    self.connected = False
                    break
                
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line:
                        self.process_server_message(json.loads(line))
                        
            except json.JSONDecodeError as e:
                print(f"Invalid JSON from server: {e}")
            except Exception as e:
                print(f"Error receiving from server: {e}")
                self.connected = False
                break
    
    def process_server_message(self, message):
        """Process a message from the server"""
        msg_type = message.get('type')
        
        if msg_type == 'assignment':
            self.player_idx = message.get('player_idx')
            self.my_color = message.get('color')
            print(f"Assigned as Player {self.player_idx} ({self.my_color})")
            
        elif msg_type == 'game_state':
            # Update game state
            self.update_game_state(message)
            
        elif msg_type == 'error':
            print(f"Error from server: {message.get('message')}")
    
    def update_game_state(self, state):
        """Update local game state from server"""
        # Update board
        board_data = state.get('board', [])
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                piece_data = board_data[y][x]
                if piece_data is None:
                    self.board[y][x] = None
                else:
                    piece_type = PieceType.KITTEN if piece_data['type'] == 'KITTEN' else PieceType.CAT
                    piece_color = PieceColor.ORANGE if piece_data['color'] == 'ORANGE' else PieceColor.BLACK
                    self.board[y][x] = Piece(piece_type, piece_color)
        
        self.whoseturn = state.get('whoseturn', 0)
        self.orange_cats = state.get('orange_cats', 0)
        self.black_cats = state.get('black_cats', 0)
        self.win_msg = state.get('win_msg', "")
        self.last_placed_pos = tuple(state.get('last_placed_pos', (-1, -1)))
    
    def send_move(self, x, y, piece_type):
        """Send a move to the server"""
        if not self.connected:
            return
        
        move = {
            'type': 'move',
            'x': x,
            'y': y,
            'piece_type': piece_type.name
        }
        
        try:
            msg = json.dumps(move) + '\n'
            self.socket.sendall(msg.encode('utf-8'))
        except Exception as e:
            print(f"Error sending move: {e}")
            self.connected = False
    
    def mouse_to_board_pos(self, mouse_x, mouse_y):
        """Convert mouse position to board coordinates"""
        board_x = (mouse_x - BOARD_START_X) // CELL_SIZE
        board_y = (mouse_y - BOARD_START_Y) // CELL_SIZE
        
        if 0 <= board_x < BOARD_SIZE and 0 <= board_y < BOARD_SIZE:
            return board_x, board_y
        return None, None
    
    def handle_click(self, mouse_x, mouse_y):
        """Handle mouse clicks"""
        if not self.connected or self.player_idx is None:
            return
        
        if self.win_msg:
            return
        
        if self.whoseturn != self.player_idx:
            return
        
        # Check piece selection
        ocat_rect = pygame.Rect(30, 480, 96, 96)
        okitten_rect = pygame.Rect(30, 580, 96, 96)
        bcat_rect = pygame.Rect(1050, 480, 96, 96)
        bkitten_rect = pygame.Rect(1050, 580, 96, 96)
        
        if self.player_idx == 0:  # Orange
            if ocat_rect.collidepoint(mouse_x, mouse_y) and self.orange_cats > 0:
                self.selected_piece = PieceType.CAT
                return
            elif okitten_rect.collidepoint(mouse_x, mouse_y):
                self.selected_piece = PieceType.KITTEN
                return
        else:  # Black
            if bcat_rect.collidepoint(mouse_x, mouse_y) and self.black_cats > 0:
                self.selected_piece = PieceType.CAT
                return
            elif bkitten_rect.collidepoint(mouse_x, mouse_y):
                self.selected_piece = PieceType.KITTEN
                return
        
        # Check board click
        board_x, board_y = self.mouse_to_board_pos(mouse_x, mouse_y)
        if board_x is not None and self.board[board_y][board_x] is None:
            self.send_move(board_x, board_y, self.selected_piece)
    
    def draw_board(self):
        """Draw the game board"""
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                rect = pygame.Rect(
                    BOARD_START_X + x * CELL_SIZE,
                    BOARD_START_Y + y * CELL_SIZE,
                    CELL_SIZE, CELL_SIZE
                )
                pygame.draw.rect(self.screen, LIGHT_BLUE, rect)
                pygame.draw.rect(self.screen, BLACK, rect, 2)
        
        # Draw pieces
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                piece = self.board[y][x]
                center_x = BOARD_START_X + x * CELL_SIZE + CELL_SIZE // 2
                center_y = BOARD_START_Y + y * CELL_SIZE + CELL_SIZE // 2
                
                if piece is not None:
                    if piece.color == PieceColor.ORANGE:
                        sprite = self.cat_o_sprite if piece.type == PieceType.CAT else self.kitten_o_sprite
                    else:
                        sprite = self.cat_b_sprite if piece.type == PieceType.CAT else self.kitten_b_sprite
                    
                    sprite_rect = sprite.get_rect(center=(center_x, center_y))
                    self.screen.blit(sprite, sprite_rect)
                
                if (x, y) == self.last_placed_pos:
                    outline_rect = self.cat_o_sprite.get_rect(center=(center_x, center_y))
                    pygame.draw.rect(self.screen, WHITE, outline_rect, width=2)
    
    def draw_ui(self):
        """Draw UI elements"""
        # Title
        text = self.large_font.render("boop.", True, BLUE)
        self.screen.blit(text, (620, 20))
        
        # Connection status
        if not self.connected:
            text = self.font.render("Disconnected from server", True, (255, 0, 0))
            self.screen.blit(text, (500, 80))
        elif self.player_idx is None:
            text = self.font.render("Waiting for assignment...", True, WHITE)
            self.screen.blit(text, (500, 80))
        
        # Win message
        if self.win_msg:
            text = self.large_font.render(self.win_msg, True, BLUE)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 750))
            self.screen.blit(text, text_rect)
            return
        
        # Turn indicator
        if self.whoseturn == 0:
            pygame.draw.rect(self.screen, NAVY, (25, 125, 280, 100))
            turn_text = "Orange's turn!"
            text = self.large_font.render(turn_text, True, ORANGE)
            self.screen.blit(text, (50, 150))
        else:
            turn_text = "Orange"
            text = self.large_font.render(turn_text, True, ORANGE)
            self.screen.blit(text, (50, 150))
        
        if self.whoseturn == 1:
            pygame.draw.rect(self.screen, NAVY, (1025, 125, 280, 100))
            turn_text = "Black's turn!"
            text = self.large_font.render(turn_text, True, BLACK)
            self.screen.blit(text, (1050, 150))
        else:
            turn_text = "Black"
            text = self.large_font.render(turn_text, True, BLACK)
            self.screen.blit(text, (1050, 150))
        
        # Cats and kittens display
        text = self.font.render(f"cats: {self.orange_cats}", True, ORANGE)
        self.screen.blit(text, (30, 450))
        text = self.font.render("kittens: inf", True, ORANGE)
        self.screen.blit(text, (30, 680))
        
        text = self.font.render(f"cats: {self.black_cats}", True, BLACK)
        self.screen.blit(text, (1050, 450))
        text = self.font.render("kittens: inf", True, BLACK)
        self.screen.blit(text, (1050, 680))
        
        # Draw piece selection
        self._draw_piece_selection()
    
    def _draw_piece_selection(self):
        """Draw piece selection UI"""
        grayed_cat_o = self.cat_o_sprite.copy()
        grayed_cat_o.set_alpha(100)
        grayed_kitten_o = self.kitten_o_sprite.copy()
        grayed_kitten_o.set_alpha(100)
        grayed_cat_b = self.cat_b_sprite.copy()
        grayed_cat_b.set_alpha(100)
        grayed_kitten_b = self.kitten_b_sprite.copy()
        grayed_kitten_b.set_alpha(100)
        
        # Orange pieces
        if self.whoseturn == 0 and self.player_idx == 0:
            self.screen.blit(self.cat_o_sprite if self.orange_cats > 0 else grayed_cat_o, (30, 480))
            self.screen.blit(self.kitten_o_sprite, (30, 580))
        else:
            self.screen.blit(grayed_cat_o, (30, 480))
            self.screen.blit(grayed_kitten_o, (30, 580))
        
        # Black pieces
        if self.whoseturn == 1 and self.player_idx == 1:
            self.screen.blit(self.cat_b_sprite if self.black_cats > 0 else grayed_cat_b, (1050, 480))
            self.screen.blit(self.kitten_b_sprite, (1050, 580))
        else:
            self.screen.blit(grayed_cat_b, (1050, 480))
            self.screen.blit(grayed_kitten_b, (1050, 580))
        
        # Selection box
        if self.player_idx == 0 and self.whoseturn == 0:
            rect = pygame.Rect(30, 580 if self.selected_piece == PieceType.KITTEN else 480, 96, 96)
            pygame.draw.rect(self.screen, BLUE, rect, width=2)
        elif self.player_idx == 1 and self.whoseturn == 1:
            rect = pygame.Rect(1050, 580 if self.selected_piece == PieceType.KITTEN else 480, 96, 96)
            pygame.draw.rect(self.screen, BLUE, rect, width=2)
    
    def draw(self):
        """Draw everything"""
        self.screen.fill(GRAY)
        self.draw_board()
        self.draw_ui()
        pygame.display.flip()
    
    def run(self):
        """Main client loop"""
        if not self.connect():
            print("Failed to connect to server")
            return
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_click(event.pos[0], event.pos[1])
            
            self.draw()
            self.clock.tick(60)
        
        if self.socket:
            self.socket.close()
        pygame.quit()

if __name__ == "__main__":
    import sys
    
    # Default values
    host = 'localhost'
    port = 5555
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print(f"Invalid port '{sys.argv[2]}', using default: {port}")
    
    print(f"Connecting to {host}:{port}")
    client = HumanClient(host=host, port=port)
    client.run()