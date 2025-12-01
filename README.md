# Boop

## Background
The original code for this gameplay was written by Dr. Kenrick Mock of UAA and presented to the AI and robotics club as a demonstration of heuristics.

The main branch of this repository is the code written by Dr. Mock, and branches from it are the work of Thatcher King and Spencer Douthit

Using the existing structure of the game, we created scripts for: 
 - Data collection using Monte Carlo sampling
 - Encoding and decoding of move positions for efficient storage
 - Construction of a Trie class to store our sampling data
 - Creation of a function to quantify the quality of a move based on the outcomes and their distance from the current state
 - Many helper functions to help describe the data stored in the Trie
 - Functionality for the orange AI agent to use an alternate, Trie value for decision making instead of the default heuristic function from the board state

## Our work
Our project is improving an AI agent’s playing ability of the game “Boop.” Boop is a board game that is available in a phyical form for but also exists digitally, written in python using pygame. The game has an AI agent player that utilizes minimax to create a search tree of moves. The board is 6x6, and building a search tree of all the possible moves gets computationally large and slow beyond a depth of 3 moves. 

In our project, we want to try a different approach to selecting a move. Instead of choosing a move using minimax and a large search space want to be able to build a dataset that can select a move in O(n) possible moves instead of n^k (where k is the search depth of the moves in the future). We will use monte carlo sampling to build a Trie data structure that indicates how good a move is based on outcomes of previous games. In our implementation, we will start with the objective of finding three kittens in a row. Even though this is not the end state of the game, it is less complex and less computationally intensive. After implementing thi,s we can modify the approach to work for complete games

To implement this Monte Carlo search, we will create a queue of moves. The queue will be a collection of moves leading up to our state. When a three-in-a-row case is identified, we will store the content of the queue as a sequence in a file. After a sufficient number of sequences collected we will use those to build a trie of all the game plays. We will analyze the trie for patterns leading to our target three-in-a-row sequence. Because our board has no particular directionality, we may be able to condense the number of sequences by combining duplicates of orientations.

While building the Trie, we use the winner outcome and distance to the end state to evaluate how good a player's position is on the board.

## Running the game
 - The game requires the pygame package to be installed. Create a virtual environment in the project folder and use 'pip install pygame' in your activated environment to install it.
 - Clone the **trie_builder** branch
 - Navigate to the game_files folder within the project and run main.py
 - When main.py runs, a game is played between two AI agents. The orange agent uses the values in the Trie structure to make move choices, while Black uses the default heuristic from Dr. Mock's implementation. If the path of the game deviates from known paths during data collection, orange reverts to the original default heuristic.
 - The GUI shows a visual representation of the game, while the text output gives data about heuristic values of selected moves and whether the agent is using the trie for move selection or the old default value.
 - This will run 10 games by default and output stats at the end of the run. It may take a few minutes to get through the games.

## Rough Idea
- Simulate several games of Boop, tracking moves taken using a queue
- Once a terminal state is found (in our case, 3 kittens in a row), save the sequence of moves in a file to build a trie
- Consider also searching for specific patterns across the board, flipping in the x and y dimension to account for various orientations of the same pattern (to be explored at some future date)

## Phases
 - Simulation and Sequence Collection
   - finding space efficient ways to store the data in either a collection of sequences or a trie object
 - Trie Creation and storage and their space and time complexity
 - Value assignment based on the data from the monte carlo sampling.
