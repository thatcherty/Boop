import pickle
import os
import random

# Define the names of our files
SEQUENCES_FILENAME = 'sequences.txt'
TRIE_FILENAME = "sampling_trie.pkl"

class TrieNode:
    def __init__(self, value = 0):
        self.children = {}
        self.heuristic_value = value

    def print_children(self):
            print(f"print values of children of pickled trie root: ")
            if not self.children:
                print("No children, this is a leaf node")
            for move, node in self.children.items():
                print(f"move: ", move, ":", decode_position(move), 
                    "value: ", node.heuristic_value
                )

class Trie:
    def __init__(self):
        """
        Initializes the Trie with a root node.
        """
        self.root = TrieNode()

    def insert_sequence(self, sequence: str) -> bool:
        """
        Inserts a sequence into the Trie.
        """
        current_node = self.root
        #check to see if this sequence already is loaded into the trie
        #if this sequence is already in the trie we don't want to influence the values again
        if self.search(sequence):
            return False
        else:
            sequence_length = len(sequence)
            winner = (sequence_length % 2) # game winner is 1 for orange or 0 for black
        
        # create heuristic values for each node based on outcomes from games
        for index, move in enumerate(sequence):
            if move not in current_node.children:
                current_node.children[move] = TrieNode()
            
            # creates value between 0 and 1 to add to the heuristic value
            # large enough sampling should eventually collect good moves
            value = 1/(index - sequence_length) 
            if winner == 0:
                value *= -1 #give negative value to indicate good black player outcome

            # updating heuristic value based on new input sequence
            current_node.children[move].heuristic_value += value
            current_node = current_node.children[move]
        
        return True

    def search(self, sequence: str) -> bool: #Returns True if the full sequence is stored in the trie.
        current_node = self.root
        for move in sequence:
            if move not in current_node.children:
                return False
            current_node = current_node.children[move]
        if not current_node.children:
            return True #If there are no children at the end of the sequence then it must be a leaf node
        return False
    
    def pickle_trie(self): # takes trie and pickles to file
        with open("sampling_trie.pkl", "wb") as file:
            pickle.dump(self, file)
        print("trie pickled to: ", TRIE_FILENAME, "\n" )

    def print_sequence_analysis(self, sequence = ""): # traverses a sequence to see the data related to a specific or random path
        if sequence: # if a sequence is specified
            print("\n", "Traversing a path for sequence:", sequence)
            current_node = self.root
            for move in sequence:
                print(
                    "Number of possible moves in trie:", len(current_node.children),
                    "Move:", move, ":", decode_position(move), 
                    "Value for next move:", current_node.children[move].heuristic_value                    
                )
                current_node = current_node.children[move]
        else:
            print("\n", "Traversing a random path:")
            current_node = self.root
            while current_node.children:
                random_child = random.choice(list(current_node.children.items()))
                child_next_move, child_next_node = random_child
                print(
                    "Number of possible moves in trie:", len(current_node.children),
                    "Move:", child_next_move, ":", decode_position(child_next_move), 
                    "Value for next move:", child_next_node.heuristic_value,
                )
                current_node = child_next_node

def prepare_trie(load_from_sequences_file = True): #load_from_sequences toggles whether to update the trie from sequences.txt
    if TRIE_FILENAME in os.listdir("./"):
        print(TRIE_FILENAME, " found! ...loading ", TRIE_FILENAME)
        game_trie = load_pickled_trie(TRIE_FILENAME)
        if load_from_sequences_file == True:
            print("updating trie from ", SEQUENCES_FILENAME)
            import_sequences_to_trie(game_trie)
            game_trie.pickle_trie()
    else:
        print(TRIE_FILENAME, " not found! Building new trie and pickling to ", TRIE_FILENAME, "\n")
        game_trie = Trie()
        if SEQUENCES_FILENAME in os.listdir("./"):
            import_sequences_to_trie(game_trie)
            game_trie.pickle_trie()
        else:
            print("Sequence data not found. Returning empty Trie object")
    return game_trie

def encode_position(x,y): #take in integer postions and output a single character
    return chr(6*x + y + 65)

def decode_position(char): #translates from char to (x,y) coordinate
    x = (ord(char)-65) // 6
    y = (ord(char)-65) % 6
    return (x,y)

def append_output_file(outputString): #outputString represents an encoded sequence of moves
    try:
        # 'a' mode means 'append' - it will add to the existing file.
        with open(SEQUENCES_FILENAME, 'a', newline='') as txtfile:
            txtfile.write(outputString + '\n')
            #print("Data saved successfully.")
    except IOError as e:
        print(f"Error saving file: {e}")

def import_sequences_to_list() -> list: # takes sequences file and returns a list of sequences
    sequences = []
    try:
        with open(SEQUENCES_FILENAME, 'r') as file:
            for line in file:
                sequences.append(line.strip())
    except FileNotFoundError:
        print(f"Error: The file '{SEQUENCES_FILENAME}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return sequences

def import_sequences_to_trie(game_trie): #imports all data from txt file and loads it into the trie
    counter = 0
    lines = 0
    try:
        with open(SEQUENCES_FILENAME, 'r') as file:
            for line in file:
                # insert the sequence into the trie and add to counter if sequence is unique
                if game_trie.insert_sequence(line.strip()):
                    counter += 1
                lines += 1 #tracks total number of lines in file
    except FileNotFoundError:
        print(f"Error: The file '{SEQUENCES_FILENAME}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    print(counter, "new sequences added to Trie in memory from", lines, "sequences in file")

def load_pickled_trie(trieFilename: str) -> Trie: # loads a pickle file into a Trie data type
        with open(trieFilename, "rb") as file:
            loaded_trie = pickle.load(file)
        print("Data loaded from ", trieFilename)
        return loaded_trie