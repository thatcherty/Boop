import json
import os

# Define the name of our JSON file
FILENAME = 'sequences.json'

def save_to_json(data, filename):

    """Saves a dictionary to a JSON file."""
    print()
    print(f"--- Saving data to {filename} ---")
    try:
        # 'w' mode means 'write' - it will overwrite the file if it exists.
        with open(filename, 'w', encoding='utf-8') as f:
            # json.dump() writes the data to the file object 'f'
            # indent=4 makes the JSON file human-readable (pretty-prints it)
            json.dump(data, f, indent=2)
        print("Data saved successfully.")
    except IOError as e:
        print(f"Error saving file: {e}")

# def load_from_json(filename):
#     """Loads a dictionary from a JSON file."""
#     print(f"--- Loading data from {filename} ---")
#     try:
#         # Check if the file exists first
#         if not os.path.exists(filename):
#             print(f"File {filename} not found. Returning empty dictionary.")
#             return {}
            
#         # 'r' mode means 'read'
#         with open(filename, 'r', encoding='utf-8') as f:
#             # json.load() reads the data from the file object 'f'
#             data = json.load(f)
#             print("Data loaded successfully.")
#             return data
#     except json.JSONDecodeError:
#         print(f"Error: Could not decode JSON from {filename}. Returning empty dictionary.")
#         return {}
#     except IOError as e:
#         print(f"Error loading file: {e}")
#         return {}
