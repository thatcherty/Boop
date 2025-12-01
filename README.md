# Running the game
 - The game requires the pygame package to be installed. Create a virtual environment in the project folder and use 'pip install pygame' in your activated environment to install it.
 - Clone the **trie_builder** branch
 - Navigate to the game_files folder within the project and run main.py
 - When main.py runs, a game is played between two AI agents. The orange agent uses the values in the Trie structure to make move choices, while Black uses the default heuristic from Dr. Mock's implementation. If the path of the game deviates from known paths during data collection, orange reverts to the original default heuristic.
 - The GUI shows a visual representation of the game, while the text output gives data about heuristic values of selected moves and whether the agent is using the trie for move selection or the old default value.
 - This will run 10 games by default and output stats at the end of the run. It may take a few minutes to get through the games.