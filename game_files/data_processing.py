import pickle
import os

# Define the name of our files
SEQUENCES_FILENAME = 'sequences.txt'
TRIE_FILENAME = "sampling_trie.pkl"

def encode_position(x,y): #take in integetr postions and output a single character
    return chr(6*x + y + 65)

def decode_position(char):
    x = (ord(char)-65) // 6
    y = (ord(char)-65) % 6
    return (x,y)


def append_output_file(outputString): #outputString represents an encoded sequence of moves
     
    """Saves a encoded sequence as a string into a new line of the csv file"""
    print()
    print(f"--- Saving data to {SEQUENCES_FILENAME} ---")
    try:
        # 'a' mode means 'append' - it will add to the existing file.
        with open(SEQUENCES_FILENAME, 'a', newline='') as txtfile:
            txtfile.write(outputString + '\n')
            print("Data saved successfully.")
    except IOError as e:
        print(f"Error saving file: {e}")

def import_sequences_to_list():
    sequences = []
    try:
        with open(SEQUENCES_FILENAME, 'r') as file:
            for line in file:
                # insert the sequence into the trie
                sequences.append(line.strip())
    except FileNotFoundError:
        print(f"Error: The file '{SEQUENCES_FILENAME}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return sequences

def import_sequences_to_trie(game_trie): #imports data from txt file and returns a list of sequences.
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

def load_pickled_trie(trieFilename: str):
        with open(trieFilename, "rb") as file:
            loaded_trie = pickle.load(file)
        print("Data loaded from ", trieFilename)
        return loaded_trie



class TrieNode:
    def __init__(self, value = 0):
        self.children = {}
        self.heuristic_value = value


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

    def search(self, sequence: str) -> bool:
        """
        Returns True if the full sequence is stored in the trie.
        """
        current_node = self.root
        for move in sequence:
            if move not in current_node.children:
                return False
            current_node = current_node.children[move]
        if not current_node.children:
            return True #If there are no children at the end of the sequence then it must be a leaf node
        return False
    
    def pickle_trie(self):
        """
        takes trie and pickles to file
        """
        with open("sampling_trie.pkl", "wb") as file:
            pickle.dump(self, file)
        print("trie pickled to: ", TRIE_FILENAME, "\n" )

def prepare_trie():
    if TRIE_FILENAME in os.listdir("./"):
        print(TRIE_FILENAME, " found! ...loading ", TRIE_FILENAME)
        game_trie = load_pickled_trie(TRIE_FILENAME)
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