from game import BoopGame
from pieces import PlayerType # Import PlayerType from pieces
from data_processing import append_output_file

def collect_sequences(rounds_played, ai_depth_setting):
    max_sequence_length = 60 # store no sequences longer than 60 moves into sequences.txt

    round_counter = 0
    while round_counter < rounds_played: 
        print(f"\nPlaying Game number: ", round_counter)
        game = BoopGame(ai_depth=ai_depth_setting)
        game.player0 = PlayerType.AI   # Player 0 (Orange) type: HUMAN or AI
        game.player1 = PlayerType.AI   # Player 1 (Black) type: HUMAN or AI

        while game.win_msg == "":
                current_player_type = game.player0 if game.whoseturn == 0 else game.player1
                game.make_ai_move()
                if len(game.sequence) > max_sequence_length :
                    game.win_msg == "Too long! Rejected data!"
                    game.sequence = ""
                    break
        round_counter += 1
        if game.sequence:
            append_output_file(game.sequence) #Store the sequence in a txt file