# This class implements the server portion of the boop game.
# The first client to connect is orange and the second is black.
# The default port is 5555.  
#
import pygame
import socket
import threading
import json
import sys
from game import BoopGame
from gui import GameGUI
from pieces import PieceType, PieceColor

class BoopServer:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.game = BoopGame(ai_depth=1)  # Create game instance
        self.gui = GameGUI(self.game)
        
        self.clients = []  # List of (connection, address, player_idx)
        self.client_lock = threading.Lock()
        
        self.running = True
        
    def start(self):
        """Start the server"""
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(2)

            # Get and display server IP addresses
            import socket as sock
            hostname = sock.gethostname()
            try:
                local_ip = sock.gethostbyname(hostname)
                print(f"Server started on {self.host}:{self.port}")
                print(f"Hostname: {hostname}")
                print(f"Local IP: {local_ip}")
            except:
                print(f"Server started on {self.host}:{self.port}")
            
            # Try to get all network interfaces
            try:
                import socket as sock
                s = sock.socket(sock.AF_INET, sock.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                network_ip = s.getsockname()[0]
                s.close()
                if network_ip != local_ip:
                    print(f"Network IP: {network_ip}")
            except:
                pass

            print("Waiting for 2 players to connect...")
            
            # Start accepting connections in a separate thread
            accept_thread = threading.Thread(target=self.accept_connections)
            accept_thread.daemon = True
            accept_thread.start()
            
            # Run the game loop
            self.game_loop()
            
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.cleanup()
    
    def accept_connections(self):
        """Accept client connections"""
        while self.running and len(self.clients) < 2:
            try:
                self.server_socket.settimeout(1.0)
                try:
                    conn, addr = self.server_socket.accept()
                    with self.client_lock:
                        player_idx = len(self.clients)
                        self.clients.append((conn, addr, player_idx))
                        print(f"Player {player_idx} ({['Orange', 'Black'][player_idx]}) connected from {addr}")
                        
                        # Send player assignment
                        self.send_to_client(conn, {
                            'type': 'assignment',
                            'player_idx': player_idx,
                            'color': ['orange', 'black'][player_idx]
                        })
                        
                        # Start listening thread for this client
                        client_thread = threading.Thread(
                            target=self.handle_client,
                            args=(conn, addr, player_idx)
                        )
                        client_thread.daemon = True
                        client_thread.start()
                        
                        if len(self.clients) == 2:
                            print("Both players connected! Game starting...")
                    
                    # Broadcast initial state outside of lock
                    if len(self.clients) == 2:
                        import time
                        time.sleep(0.2)  # Give clients time to process assignment
                        self.broadcast_game_state()
                        
                except socket.timeout:
                    continue
            except Exception as e:
                if self.running:
                    print(f"Error accepting connection: {e}")
    
    def handle_client(self, conn, addr, player_idx):
        """Handle messages from a client"""
        buffer = ""
        while self.running:
            try:
                data = conn.recv(4096).decode('utf-8')
                if not data:
                    print(f"Player {player_idx} disconnected")
                    break
                
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line:
                        self.process_client_message(json.loads(line), player_idx)
                        
            except json.JSONDecodeError as e:
                print(f"Invalid JSON from player {player_idx}: {e}")
            except Exception as e:
                print(f"Error handling player {player_idx}: {e}")
                break
        
        # Client disconnected
        with self.client_lock:
            self.clients = [(c, a, p) for c, a, p in self.clients if p != player_idx]
    
    def process_client_message(self, message, player_idx):
        """Process a message from a client"""
        msg_type = message.get('type')
        
        if msg_type == 'move':
            # Verify it's the correct player's turn
            if self.game.whoseturn != player_idx:
                self.send_to_player(player_idx, {
                    'type': 'error',
                    'message': 'Not your turn'
                })
                return
            
            if self.game.win_msg:
                self.send_to_player(player_idx, {
                    'type': 'error',
                    'message': 'Game is over'
                })
                return
            
            x = message.get('x')
            y = message.get('y')
            piece_type_str = message.get('piece_type')
            
            # Convert piece_type string to enum
            piece_type = PieceType.KITTEN if piece_type_str == 'KITTEN' else PieceType.CAT
            
            # Validate move
            if not self.validate_move(x, y, piece_type, player_idx):
                self.send_to_player(player_idx, {
                    'type': 'error',
                    'message': 'Invalid move'
                })
                return
            
            # Process the move
            success = self.game.process_move(x, y, piece_type)
            
            if success:
                # Broadcast updated game state to all clients
                self.broadcast_game_state()
    
    def validate_move(self, x, y, piece_type, player_idx):
        """Validate that a move is legal"""
        # Check bounds
        if not (0 <= x < 6 and 0 <= y < 6):
            return False
        
        # Check if cell is empty
        if not self.game.is_empty(x, y):
            return False
        
        # Check if player has cats available if placing a cat
        if piece_type == PieceType.CAT:
            if player_idx == 0 and self.game.orange_cats <= 0:
                return False
            if player_idx == 1 and self.game.black_cats <= 0:
                return False
        
        return True
    
    def send_to_client(self, conn, message):
        """Send a message to a specific client connection"""
        try:
            msg = json.dumps(message) + '\n'
            conn.sendall(msg.encode('utf-8'))
        except Exception as e:
            print(f"Error sending to client: {e}")
    
    def send_to_player(self, player_idx, message):
        """Send a message to a specific player by index"""
        with self.client_lock:
            for conn, addr, p_idx in self.clients:
                if p_idx == player_idx:
                    self.send_to_client(conn, message)
                    break
    
    def broadcast_game_state(self):
        """Send current game state to all clients"""
        # Serialize board
        board_data = []
        for row in self.game.board:
            row_data = []
            for piece in row:
                if piece is None:
                    row_data.append(None)
                else:
                    row_data.append({
                        'type': piece.type.name,
                        'color': piece.color.name
                    })
            board_data.append(row_data)
        
        state = {
            'type': 'game_state',
            'board': board_data,
            'whoseturn': self.game.whoseturn,
            'orange_cats': self.game.orange_cats,
            'black_cats': self.game.black_cats,
            'win_msg': self.game.win_msg,
            'last_placed_pos': self.game.last_placed_pos
        }
        
        print(f"Broadcasting game state: Turn={self.game.whoseturn}, Win={self.game.win_msg}")
        
        with self.client_lock:
            for conn, addr, player_idx in self.clients:
                self.send_to_client(conn, state)
    
    def game_loop(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        
        while self.running:
            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
            
            # Draw the game state
            self.gui.draw()
            clock.tick(60)
        
        pygame.quit()
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        with self.client_lock:
            for conn, addr, player_idx in self.clients:
                try:
                    conn.close()
                except:
                    pass
        try:
            self.server_socket.close()
        except:
            pass
        print("Server shut down")

if __name__ == "__main__":
    server = BoopServer(host='localhost', port=5555)
    server.start()