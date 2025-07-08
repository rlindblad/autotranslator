#!/usr/bin/env python3
"""Main entry point for the autotranslator program."""

import os
import sys
import pandas as pd
import llm


def read_localizations(file_path="localizations.xlsx"):
    """
    Read the localizations Excel file and return a DataFrame.

    Args:
        file_path (str): Path to the Excel file containing localizations.

    Returns:
        pd.DataFrame: DataFrame containing the localization data.
    """
    try:
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found.")
            return None

        # Read the Excel file
        df = pd.read_excel(file_path)
        print(f"Successfully loaded {len(df)} localization entries.")
        return df
    except Exception as e:
        print(f"Error reading localizations file: {e}")
        return None


def translate_text(text, source_lang, target_lang):
    """
    Translate text using an LLM.

    Args:
        text (str): Text to translate.
        source_lang (str): Source language code.
        target_lang (str): Target language code.

    Returns:
        str: Translated text.
    """
    try:
        model = llm.get_model("qwen3")
        prompt = f"Translate the following text from {source_lang} to {target_lang}:\n\n{text}"

        response = model.prompt(prompt)
        return response.text().strip()
    except Exception as e:
        print(f"Error during translation: {e}")
        return None


def main():
    """Main entry point for the autotranslator program."""
    print("Autotranslator initialized!")

    # Get the path to the localizations file
    file_path = "localizations.xlsx"
    if len(sys.argv) > 1:
        file_path = sys.argv[1]

    # Read the localizations
    df = read_localizations(file_path)

    if df is not None:
        print(f"Columns in the file: {', '.join(df.columns)}")
        # Display the first few rows
        print("\nSample data:")
        print(df.head())
    else:
        print("Failed to read localizations file.")


if __name__ == "__main__":
    main()
