# Boop
Our project is improving an AI agent’s playing ability of the game “Boop.” Boop is a board game that is available in a phyical form for but also exists digitally, written in python using pygame. The game has an AI agent player that utilizes minimax to create a search tree of moves. The board is 6x6, and building a search tree of all the possible moves gets computationally large and slow beyond a depth of 3 moves. 

In our project, we want to prune the search tree so we can search deeper but maintain a reasonable speed of search. We will implement alpha beta pruning but also try to identify sequences that will lead to wins or highly adventageous moves. In the game, getting three kitten or cats in a row is important for winning, so we will use monte carlo sampling to find the sequences that will lead to this outcome. Games will be played between two automated agents randomly, and if a sequence leads to three in a row, the preceeding moves will be stored for analysis later. Using this analysis, we can create a heuristic function for the AI agent that encourages these advantageous sequences.

To implement this Monte Carlo search, we will create a queue of moves. The size of the queue will be limited to the number of preceding steps we are looking at. When a three-in-a-row case is identified, we will store the content of the queue as a sequence in a trie. After a sufficient number of sequences are identified, we will analyze the trie for patterns leading to our target three-in-a-row sequence. Because our board has no particular directionality, we may be able to condense the number of sequences by combining duplicates of orientations.

Using this data of sequences we will provide a heuristic that evaluates how good a players position is on the board by how close they are to our target sequences. We will also implement pruning to the search tree to eliminate moves that are unlikely to lead to our target.

## Rough Idea
- Simulate several games of Boop, tracking moves taken using a queue
- Once an ideal scenario has been found, for example, 3 kittens or cats in a row, save those moves in a tree (or other structure)
- Consider the use of [Alpha-Beta Pruning](https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning) to decrease the moves searched
- Consider also searching for specific patterns across the board, flipping in various directions to account for various orientations of the same pattern

## Some ideal scenarios
 - 3 Kittens in a row (get 3 cats)
 - 3 Cats in a row (win)
 - 8 Cats on the board (win)

## Phases
 - Simulation and Sequence Collection
   - Consider collecting what cat or kitten was played
   - Numerical values for what cat or kitten is on the board
   - Benchmarking collection to identify average move time and average win time
 - Generalization
 - Hueristic Creation

## Note
The game itself, the sprites, sound effects, and general gameplay were not written by us. We have modified portions of the code to support new logic using new data structures in hopes of creating a more effective AI. The changes can be seen in the commit history.
