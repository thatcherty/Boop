# This class implements the networking/logic portion of a randomly playing client.
# It is a template that you could use to build a more intelligent client, or use
# as testing against an opponent that plays poorly.
#
# Run with python client_random.py <host> <port>
# The default host is localhost and the port is 5555
#
import socket
import json
import random
import time
import threading
from pieces import PieceType, PieceColor, Piece
from constants import BOARD_SIZE

class RandomClient:
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
        
        self.running = True
        self.connected = False
        
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
            print(f"Game state received. Turn: {self.whoseturn}, My idx: {self.player_idx}, Win: {self.win_msg}")
            
            # Make a move if it's our turn
            if self.whoseturn == self.player_idx and not self.win_msg:
                print(f"It's my turn! Making a move...")
                time.sleep(0.5)  # Small delay to simulate thinking
                self.make_random_move()
            else:
                if self.win_msg:
                    print(f"Game over: {self.win_msg}")
                else:
                    print(f"Waiting for opponent (Player {self.whoseturn})")
            
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
    
    def get_valid_moves(self):
        """Get all valid moves for current player"""
        moves = []
        
        # Determine available piece types
        available_types = [PieceType.KITTEN]
        if (self.player_idx == 0 and self.orange_cats > 0) or \
           (self.player_idx == 1 and self.black_cats > 0):
            available_types.append(PieceType.CAT)
        
        # Find all empty cells
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                if self.board[y][x] is None:
                    for piece_type in available_types:
                        moves.append((x, y, piece_type))
        
        return moves
    
    def make_random_move(self):
        """Make a random valid move"""
        valid_moves = self.get_valid_moves()
        
        if not valid_moves:
            print("No valid moves available")
            return
        
        # Pick a random move
        x, y, piece_type = random.choice(valid_moves)
        
        print(f"Random AI choosing: {piece_type.name} at ({x}, {y})")
        self.send_move(x, y, piece_type)
    
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
    
    def run(self):
        """Main client loop"""
        if not self.connect():
            print("Failed to connect to server")
            return
        
        print("Random AI client running. Press Ctrl+C to exit.")
        
        try:
            while self.running and self.connected:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.running = False
            if self.socket:
                self.socket.close()

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
    client = RandomClient(host=host, port=port)
    client.run()