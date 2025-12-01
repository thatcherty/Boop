# Run this file if you want to run everything locally, without a server.
# You can control if a human or AI is playing in the settings below, and how far the
# lookahead depth should be if it is AI.  
#
import pygame
import sys
from game import BoopGame
from gui import GameGUI
from pieces import PlayerType # Import PlayerType from pieces
from data_collection import collect_sequences
from data_processing import *


# Main game loop and program start
def run_game():
    print("Boop Game!")
    print("Edit main.py to select AI or Human Players and AI depth")
    print("Click on cats/kittens to select, then click on board to place")
    print("Win by getting 8 cats on the board or 3 cats in a row!")

    # Configure game settings
    ai_depth_setting = 3 # AI search depth - CHANGE UP to 3 (4 will be slow)

    #--------------------------------------
    # change this number to modify how many
    # games to play through
    #--------------------------------------
    count = 10


    # track how many games have been played
    played = 0

    # track stats about each game played
    # [winner: -1,0,1; in trie: 0,1; # of moves in the trie]
    stats = []

    while played < count:
        game = BoopGame(ai_depth=ai_depth_setting)
        game.player0 = PlayerType.AI   # Player 0 (Orange) type: HUMAN or AI
        game.player1 = PlayerType.AI   # Player 1 (Black) type: HUMAN or AI

        gui = GameGUI(game)

        print(f"Games played: {played}")

        running = True
        while running:
            gui.handle_events() # Process user input

            # Handle AI turns
            if game.win_msg == "":
                current_player_type = game.player0 if game.whoseturn == 0 else game.player1
                if current_player_type == PlayerType.AI:
                    gui.update_ai_thinking_status(True) # Show AI thinking on GUI
                    gui.draw() # Update display with "AI thinking" message
                    pygame.time.wait(200) # Small delay for visual effect
                    game.make_ai_move()
                    gui.update_ai_thinking_status(False) # AI finished thinking
                    # Re-draw the board immediately after AI move
                    gui.draw()
                    pygame.time.wait(500) # Small delay after AI move for player to see
            
            gui.draw() # Always draw the current game state
            gui.clock.tick(60)  # 60 FPS
            if game.win_msg:
                pygame.time.wait(2000) # Small delay after AI move for player to see
                break

        game.ai.heuristic_trie.print_sequence_analysis(stats, played, game.sequence)
        played += 1
        
    game_stats(stats)
    

if __name__ == "__main__":
    run_game()


