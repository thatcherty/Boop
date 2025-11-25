import json
import csv
import os

# Define the name of our JSON file
FILENAME = 'sequences.txt'

def encode_position(x,y): #take in integetr postions and output a single character
    return chr(6*x + y + 65)

def decode_position(char):
    x = (ord(char)-65) // 6
    y = (ord(char)-65) % 6
    return (x,y)


def append_output_file(outputString): #outputString represents an encoded sequence of moves
     
    """Saves a encoded sequence as a string into a new line of the csv file"""
    print()
    print(f"--- Saving data to {FILENAME} ---")
    try:
        # 'a' mode means 'append' - it will add to the existing file.
        with open(FILENAME, 'a', newline='') as txtfile:
            txtfile.write(outputString + '\n')
            print("Data saved successfully.")
    except IOError as e:
        print(f"Error saving file: {e}")

def import_sequences_to_list():
    sequences = []
    try:
        with open(FILENAME, 'r') as file:
            for line in file:
                # insert the sequence into the trie
                sequences.append(line.strip())
    except FileNotFoundError:
        print(f"Error: The file '{FILENAME}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return sequences

def import_sequences_to_trie(game_trie): #imports data from txt file and returns a list of sequences.
    try:
        with open(FILENAME, 'r') as file:
            for line in file:
                # insert the sequence into the trie
                game_trie.insert_sequence(line.strip())
    except FileNotFoundError:
        print(f"Error: The file '{FILENAME}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")



class TrieNode:
    def __init__(self):
        self.children = {}
        self.value = 0

    def contains_move(self, move):
        return move in self.children

    def get_child(self, move):
        return self.children.get(move)


class Trie:
    def __init__(self):
        """
        Initializes the Trie with a root node.
        """
        self.root = TrieNode()

    def insert_sequence(self, sequence: str) -> None:
        """
        Inserts a sequence into the Trie.
        """
        current_node = self.root

        for move in sequence:
            if move not in current_node.children:
                current_node.children[move] = TrieNode()
            current_node = current_node.children[move]

    def contains_move(self, move: str) -> bool:
        # convenience: does any sequence start with this move?
        return self.root.contains_move(move)

    def search(self, sequence: str) -> bool:
        """
        Returns True if the full sequence is stored in the trie.
        """
        current_node = self.root
        for move in sequence:
            if move not in current_node.children:
                return False
            print(move , ", ")
            current_node = current_node.children[move]
        return current_node.is_terminal





if __name__ == "__main__":
    game_trie = Trie()
    import_sequences_to_trie(game_trie)
    game_sequences = import_sequences_to_list()
    


    print(f"looking for: ", game_sequences[3])
    print(f"checking to see if sequence is contained: ", game_trie.search(game_sequences[3]))

    print(f"print first layer of trie: ", game_trie.root.children)
        