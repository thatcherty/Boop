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
        # 'w' mode means 'write' - it will overwrite the file if it exists.
        with open(FILENAME, 'a', newline='') as txtfile:
            txtfile.write(outputString + '\n')
            #csv_writer = csv.writer(csvfile)

            # Write the row to the CSV file
            #csv_writer.writerow(outputString)

            print("Data saved successfully.")
    except IOError as e:
        print(f"Error saving file: {e}")

def import_sequences(game_trie): #imports data from txt file and returns a list of sequences.
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
        """
        Initializes a TrieNode.
        children: A dictionary to store child nodes, where keys are characters and values are TrieNode objects.
        if the node has no children it is a 'three in a row'.
        """
        self.children = {}

class Trie:
    def __init__(self):
        """
        Initializes the Trie with a root node.
        """
        self.value = 0
        self.frequency = 0
        self.root = TrieNode()

    def insert_sequence(self, sequence: str) -> None:
        """
        Inserts a sequences into the Trie.
        """
        current_node = self.root
        length = len(sequence)
        winner = length % 2 # odd length strings mean orange won, even mean black won

        for move in sequence:
            if move not in current_node.children:
                current_node.children[move] = TrieNode()
            current_node = current_node.children[move]
            self.frequency += 1

            # considers the length and winner as weight
            if winner:
                self.value += (1 * length)
            else:
                self.value += (-1 * length)


    def search(self, sequence: str) -> bool:
        """
        Searches for a word in the Trie.
        Returns True if the word is found, False otherwise.
        """
        current_node = self.root
        for move in sequence:
            if sequence not in current_node.children:
                return False
            current_node = current_node.children[move]
        if not current_node.children:
            return True
        else:
            return False




if __name__ == "__main__":
    sampleTrie = Trie()
    Sequences = import_sequences()
    print(Sequences)

    for sequence in Sequences:
        sampleTrie.insert_sequence(sequence)
    
    print(f"looking for: ", Sequences[3])
    print(f"checking to see if sequence is contained: ", sampleTrie.search(Sequences[3]))

    print(f"print first layer of trie: ", sampleTrie.root.children['I'])
        