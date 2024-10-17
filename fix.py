import pandas as pd
import json
import re
import os
from anki_export import ApkgReader
import pyexcel_xlsxwx

# Global variable to store word definitions
big_data = {}

def get_text_only(definition_data):
    """
    Extract the main definition text from the raw data.

    Args:
    definition_data (list): List of strings and possibly other data types containing the definition.

    Returns:
    str: Cleaned and simplified definition.
    """
    def get_non_recursive(information):
        stack = [information]
        result = []
        while stack:
            current = stack.pop()
            if isinstance(current, str):
                result.append(current)
            elif isinstance(current, list):
                stack.extend(reversed(current))  # Reverse to preserve original order
            elif isinstance(current, dict):
                content = current.get("content")
                if content:
                    stack.append(content)
        return "".join(result)
    
    my_text = get_non_recursive(definition_data)
   
    # Remove special sections often found in dictionaries
    my_text = re.sub(r"([①-⑩❶-❿➊-➓])", r"<br/>&nbsp;\1", my_text)
    my_text = re.sub(r"（.+?）|［.+?］|〈.+?〉|《.+?》|【.+?】", "", my_text)
    # my_text = my_text.replace("アヒ――", "")
    return my_text.split("[補説]")[0]     \
           .split("📚使い方")[0]   \
           .split("［用法］")[0]

def add_to_big_data(dictionary_path):
    """
    Add words and their definitions from dictionary files to the global big_data dictionary.

    Args:
    dictionary_path (str): Path to the dictionary folder.
    """
    global big_data
    print(f"Adding {dictionary_path}")
    
    # List all files in the dictionary folder
    files = os.listdir(dictionary_path)

    # Filter files that match the pattern term_bank_X.json
    term_bank_files = [f for f in files if re.match(r"term_bank_\d+\.json", f)]
    
    # Sort files based on the number in term_bank_X.json (in case they are unordered)
    term_bank_files.sort(key=lambda x: int(re.search(r'\d+', x).group()))

    # Process each term_bank_X.json file
    for file in term_bank_files:
        print(f"Processing {file}")
        file_path = os.path.join(dictionary_path, file)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            for entry in data:
                word = re.sub(r"\[\d\]$", "", entry[0])
                second = re.sub(r"\[\d\]$", "", entry[1]) if len(entry) > 1 else None

                # Extract the definition
                definition_data = entry[5][0]["content"] if isinstance(entry[5][0], dict) else entry[5]

                # Add primary word and secondary word (if any) to big_data
                if word not in big_data:
                    big_data[word] = get_text_only(definition_data)
                if second and second not in big_data:
                    big_data[second] = get_text_only(definition_data)

                # print(big_data[word])

def cleanup_word(word, big_data):
    """
    Clean up and normalize words by removing or altering common endings to find a matching definition.

    Args:
    word (str): The word to clean up.
    big_data (dict): The dictionary containing word definitions.

    Returns:
    str: Cleaned word or original word if no match found.
    """
    if word in big_data:
        return word

    # Common endings removal logic
    endings = ["な", "だ", "と", "に", "した", "よう"]
    for ending in endings:
        if word.endswith(ending) and word[:-len(ending)] in big_data:
            return word[:-len(ending)]
    
    return word

def process_deck(deck_file, vocab_field_name, definitions_field_name):
    """
    Process an ANKI deck by adding monolingual definitions (XLSX version).

    Args:
    deck_file (str): The file name of the ANKI deck (XLSX format).
    vocab_field_name (str): The column name where the words are stored.
    """
    # Load the ANKI deck from XLSX
    deck = pd.read_excel(deck_file)

    deck.insert(0, '1', '')
    deck.insert(1, 'EnglishDef', '')

    bad_pattern = r"^.+・|\[.+?\]|.+,| |<.+?>|。|\n|\(.+?\)"

    print(f"Processing {deck_file}...")
    deck_size = len(deck)
    progress_interval = deck_size // 10  # Calculate the interval for 10% progress

    # Process each word in the deck
    for i, word in enumerate(deck[vocab_field_name]): 
        deck.loc[i, '1'] = str(i)

        word = re.sub(bad_pattern, "", word)
        word = cleanup_word(word, big_data)

        deck.loc[i, vocab_field_name] = word

        # Assign the corresponding definition if found
        deck.loc[i, "EnglishDef"] = str(deck.loc[i, definitions_field_name])
        if "sentence" not in deck.loc[i, "Notes"]:
        	deck.loc[i, definitions_field_name] = big_data.get(word, "")
    	
        if i > 0 and i % progress_interval == 0:
            progress_percentage = (i / deck_size) * 100
            print(f"Progress: {progress_percentage:.0f}%")

    print("Processing complete!")
    output_file = f"[FIXED] {deck_file}"
    deck.to_excel(output_file, index=False)
    return deck

def change_to_monolingual(deck_name):
    """
    Convert definitions in ANKI decks from bilingual to monolingual using dictionary files.
    """
    print(f"Converting {deck_name}...")

    # Convert APKG to XLSX
    with ApkgReader(f'{deck_name}.apkg') as apkg:
        pyexcel_xlsxwx.save_data(f'{deck_name}.xlsx', apkg.export(), config={'format': None})

    # Load dictionary files into big_data
    print("Loading Dictionaries")
    add_to_big_data("6. 旺文社国語辞典 第十一版")  #, 7)
    add_to_big_data("1. 大辞泉")
    add_to_big_data("2. 実用日本語表現辞典")
    add_to_big_data("4. 使い方の分かる 類語例解辞典")
    add_to_big_data("5. 故事・ことわざ・慣用句オンライン")

    # Process the deck
    print("Editing Values")
    process_deck(deck_file=f'{deck_name}.xlsx', 
                 vocab_field_name='VocabKanji', 
                 definitions_field_name='VocabDef')

    output_file = f"[FIXED] {deck_name}.xlsx"
    final_xlsx_file = pd.read_excel(output_file)

    os.remove(f'{deck_name}.xlsx')
    os.remove(output_file)

    final_xlsx_file.to_csv(f"[FIXED] {deck_name}.csv", index=False, sep = '\t')

    print(f"Conversion complete for {deck_name}!")

# Execute the conversion
change_to_monolingual("N2")
change_to_monolingual("N1")
# change_to_monolingual("N3")
