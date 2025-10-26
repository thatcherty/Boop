# Boop
Our project focuses on utilizing various data structures to improve the decision-making and speed of an AI playing Boop.

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
 - Generalization
 - Hueristic Creation
