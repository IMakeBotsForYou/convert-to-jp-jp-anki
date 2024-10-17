# Anki Deck Monolingual Conversion Script

This script processes Anki decks by converting bilingual definitions into monolingual ones using various Japanese dictionaries. It extracts definitions from dictionary files and applies them to words in the Anki deck.

## Table of Contents
1. [Overview](#overview)
2. [Usage](#usage)
3. [Dictionaries](#dictionaries)

## Overview

The script processes an Anki `.apkg` deck by:
- Exporting it to an `.xlsx` format.
- Cleaning and normalizing word entries.
- Adding definitions from Japanese dictionaries.
- Saving the processed data back into an `.xlsx` file and converting it into a `.csv`.

## Usage

To run the script, call the `change_to_monolingual(deck_name)` function, passing in the name of the Anki deck (without the `.apkg` extension). For example:

```python
change_to_monolingual("N2")
```

This will convert the `N2.apkg` deck and generate a new `[FIXED] N2.csv` file with monolingual definitions.

### Make sure to check what fields are in your decks
This code was made to be as general as possible, but still relies on some hardcoded variables. Check out the code before running.


## Dictionaries

The following dictionaries are used for definition extraction. They should be stored as JSON files in the specified directories, and their structure should follow a specific pattern.

1. **旺文社国語辞典 第十一版** (`6. 旺文社国語辞典 第十一版`)
2. **大辞泉** (`1. 大辞泉`)
3. **実用日本語表現辞典** (`2. 実用日本語表現辞典`)
4. **使い方の分かる 類語例解辞典** (`4. 使い方の分かる 類語例解辞典`)
5. **故事・ことわざ・慣用句オンライン** (`5. 故事・ことわざ・慣用句オンライン`)

Each dictionary file (e.g., `term_bank_1.json`, `term_bank_2.json`) contains word entries and their respective definitions. The script processes these entries to build a comprehensive word-definition map in the `big_data` dictionary.
