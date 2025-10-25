# This class implements the networking/logic portion of an AI-playing client.
# The AI algorithmic portion is in the ai.py file.
#
# run with:  python client_ai.py <host> <port> <lookahead_depth>
#
# The default host is localhost, 5555, with lookahead 2
#
import socket
import json
import time
import threading
from pieces import PieceType, PieceColor, Piece
from constants import BOARD_SIZE
from ai import BoopAI
from game import BoopGame

class AIClient:
    def __init__(self, host='localhost', port=5555, depth=2):
        self.host = host
        self.port = port
        self.depth = depth
        self.socket = None
        self.player_idx = None
        self.my_color = None
        
        # Game state
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.whoseturn = 0
        self.orange_cats = 0
        self.black_cats = 0
        self.win_msg = ""
        
        # Create a dummy game instance for AI to use for rule checking
        self.game = BoopGame(ai_depth=depth)
        self.ai = BoopAI(self.game, depth)
        
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
            print(f"Using Minimax AI with depth {self.depth}")
            
        elif msg_type == 'game_state':
            # Update game state
            self.update_game_state(message)
            print(f"Game state received. Turn: {self.whoseturn}, My idx: {self.player_idx}, Win: {self.win_msg}")
            
            # Make a move if it's our turn
            if self.whoseturn == self.player_idx and not self.win_msg:
                print(f"It's my turn! Computing move...")
                # Run AI computation in a separate thread to avoid blocking
                ai_thread = threading.Thread(target=self.compute_and_send_move)
                ai_thread.start()
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
    
    def compute_and_send_move(self):
        """Compute best move using AI and send it"""
        print(f"AI ({['Orange', 'Black'][self.player_idx]}) thinking...")
        start_time = time.time()
        
        # Get best move from AI
        best_move = self.ai.get_best_move(
            self.board,
            self.orange_cats,
            self.black_cats,
            self.player_idx
        )
        
        elapsed = time.time() - start_time
        
        if best_move:
            x, y, piece_type = best_move
            print(f"AI chose: {piece_type.name} at ({x}, {y}) [took {elapsed:.2f}s]")
            
            # Add small delay for visual effect
            time.sleep(0.3)
            self.send_move(x, y, piece_type)
        else:
            print("AI found no valid moves (this shouldn't happen)")
    
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
        
        print("AI client running. Press Ctrl+C to exit.")
        
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
    depth = 2
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print(f"Invalid port '{sys.argv[2]}', using default: {port}")
    if len(sys.argv) > 3:
        try:
            depth = int(sys.argv[3])
            print(f"Using AI depth: {depth}")
        except ValueError:
            print(f"Invalid depth '{sys.argv[3]}', using default: {depth}")
    
    print(f"Connecting to {host}:{port}")
    client = AIClient(host=host, port=port, depth=depth)
    client.run()