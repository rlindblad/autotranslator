#!/usr/bin/env python3
"""Main entry point for the autotranslator program."""

import os
import sys
import pandas as pd
import llm


def read_localizations(file_path="localizations.xlsx", sheet_name=None):
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
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl")
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
        prompt = (
            f"Translate the following text from {source_lang} to {target_lang}.\n\n"
            f"IMPORTANT: Return ONLY the translation itself, with no explanations, notes, or thinking process.\n\n"
            f"Text to translate: {text}"
        )

        response = model.prompt(prompt)

        # Clean up the response to extract only the translation
        translated_text = response.text().strip()

        # Remove common thinking indicators that might appear in the response
        thinking_patterns = [
            "<think>",
            "</think>",
            "Let me translate",
            "I need to translate",
            "Translating from",
            "Translating to",
            "Here's the translation",
            "The translation is:",
            "Translation:",
        ]

        for pattern in thinking_patterns:
            if pattern.lower() in translated_text.lower():
                parts = translated_text.lower().split(pattern.lower(), 1)
                if len(parts) > 1:
                    translated_text = translated_text[
                        len(parts[0]) + len(pattern) :
                    ].strip()

        # Remove any explanatory text that might appear after the translation
        if "\n\n" in translated_text:
            translated_text = translated_text.split("\n\n")[0].strip()

        return translated_text
    except Exception as e:
        print(f"Error during translation: {e}")
        return None


def get_language_code(language_name):
    """
    Convert a language name to its ISO code.

    Args:
        language_name (str): Name of the language.

    Returns:
        str: ISO code for the language.
    """
    language_map = {
        "English": "en",
        "French": "fr",
        "Spanish": "es",
        "Russian": "ru",
        "Korean": "ko",
        "German": "de",
        "Japanese": "ja",
        "Italian": "it",
        "Brazilian Portuguese": "pt-br",
        # Add more languages as needed
    }

    return language_map.get(language_name, language_name)


def translate_column(df, source_col="English", target_lang=None, retranslate=False):
    """
    Translate all rows from the source column to the target language.

    Args:
        df (pd.DataFrame): DataFrame containing the localization data.
        source_col (str): Name of the source column (default is "English").
        target_lang (str): Target language column name.
        retranslate (bool): Whether to retranslate already translated texts (default is False).

    Returns:
        pd.DataFrame: DataFrame with the translated text added to the target language column.
    """
    if df is None or source_col not in df.columns:
        print(f"Error: Source column '{source_col}' not found in the DataFrame.")
        return df

    if target_lang is None or target_lang not in df.columns:
        print(f"Error: Target language '{target_lang}' not found in the DataFrame.")
        return df

    # Create a copy to avoid modifying the original DataFrame during iteration
    result_df = df.copy()

    # Get language codes for source and target
    source_code = get_language_code(source_col)
    target_code = get_language_code(target_lang)

    print(
        f"Translating {len(df)} entries from {source_col} ({source_code}) to {target_lang} ({target_code})..."
    )

    for idx, row in df.iterrows():
        source_text = row[source_col]

        # Skip empty texts
        if pd.isna(source_text) or source_text.strip() == "":
            continue

        # Skip if target already has a translation and retranslate is False
        if (
            not retranslate
            and not pd.isna(row[target_lang])
            and row[target_lang].strip() != ""
        ):
            continue

        try:
            print(f"Translating [{idx+1}/{len(df)}]: {source_text[:30]}...")
            translated_text = translate_text(source_text, source_code, target_code)

            if translated_text:
                result_df.at[idx, target_lang] = translated_text
                print(f"  → {translated_text[:30]}...")
            else:
                print(f"  → Failed to translate.")
        except Exception as e:
            print(f"Error translating row {idx}: {e}")

    return result_df


def translate_all_languages(df, source_col="English", retranslate=False):
    """
    Translate all rows from the source column to all available language columns.

    Args:
        df (pd.DataFrame): DataFrame containing the localization data.
        source_col (str): Name of the source column (default is "English").
        retranslate (bool): Whether to retranslate already translated texts (default is False).

    Returns:
        pd.DataFrame: DataFrame with translations added to all language columns.
    """
    if df is None or source_col not in df.columns:
        print(f"Error: Source column '{source_col}' not found in the DataFrame.")
        return df

    result_df = df.copy()

    # Identify language columns (excluding source and non-language columns)
    non_language_columns = [
        "IncludeInBoth",
        "In translation",
        "Loc batch #",
        "DevEnglish",
        "Text Reviewed",
        "Text Changes",
        "Record ID",
    ]
    language_columns = [
        col
        for col in df.columns
        if col != source_col and col not in non_language_columns
    ]

    print(
        f"Found {len(language_columns)} language columns: {', '.join(language_columns)}"
    )

    # Translate to each language
    for lang_col in language_columns:
        result_df = translate_column(result_df, source_col, lang_col, retranslate)

    return result_df


def print_usage():
    """Print usage information for the autotranslator program."""
    print("\nUsage:")
    print(
        "  python -m autotranslator.main [file_path] [target_language] [sheet_name] [retranslate]"
    )
    print("\nArguments:")
    print("  file_path       - Path to the Excel file (default: localizations.xlsx)")
    print("  target_language - Target language column name or 'all' for all languages")
    print("  sheet_name      - Sheet name in the Excel file (default: Items)")
    print(
        "  retranslate     - Set to 'retranslate', 'true', 'yes', or '1' to retranslate existing translations"
    )
    print("\nExamples:")
    print("  python -m autotranslator.main localizations.xlsx French")
    print("  python -m autotranslator.main localizations.xlsx all Items retranslate")
    print("  python -m autotranslator.main input.xlsx all Sheet1")
    print(
        "\nNote: The output will be saved to a new file with '_translated' added to the filename."
    )


def main():
    """Main entry point for the autotranslator program."""
    print("Autotranslator initialized!")

    # Print usage information if no arguments are provided or help is requested
    if len(sys.argv) <= 1 or sys.argv[1] in ["--help", "-h"]:
        print_usage()
        return

    # Get the path to the localizations file
    file_path = "localizations.xlsx"
    if len(sys.argv) > 1:
        file_path = sys.argv[1]

    # Read the localizations
    sheet_name = "Items"  # Default sheet name
    if len(sys.argv) > 3:
        sheet_name = sys.argv[3]

    df = read_localizations(file_path, sheet_name)

    if df is not None:
        print(f"Columns in the file: {', '.join(df.columns)}")
        # Display the first few rows
        print("\nSample data:")
        print(df.head())

        # Check if translation is requested
        if len(sys.argv) > 2:
            target_lang = sys.argv[2]

            # Check if retranslation is requested (default is False)
            retranslate = False
            if len(sys.argv) > 4 and sys.argv[4].lower() in [
                "retranslate",
                "true",
                "yes",
                "1",
            ]:
                retranslate = True
                print(
                    "Retranslation mode: Will retranslate all text entries, including already translated ones."
                )
            else:
                print(
                    "Translation mode: Only translating entries that don't have existing translations."
                )

            # Translate to all languages if specified
            if target_lang.lower() == "all":
                translated_df = translate_all_languages(df, "English", retranslate)
            elif target_lang in df.columns:
                # Translate English to the target language
                translated_df = translate_column(
                    df, "English", target_lang, retranslate
                )
            else:
                print(f"Target language '{target_lang}' not found in the columns.")
                print(
                    f"Available languages: {[col for col in df.columns if col != 'English' and col in ['French', 'Spanish', 'Russian', 'Korean', 'German', 'Japanese', 'Italian', 'Brazilian Portuguese']]}"
                )
                print("Use 'all' to translate to all languages.")
                return

            # Create output filename (add "_translated" to the original filename)
            output_file = (
                os.path.splitext(file_path)[0]
                + "_translated"
                + os.path.splitext(file_path)[1]
            )

            # Save the translated data to the new Excel file
            try:
                print(f"Saving translations to {output_file}...")
                with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
                    translated_df.to_excel(writer, sheet_name=sheet_name, index=False)
                print("Translations saved successfully!")
            except Exception as e:
                print(f"Error saving translations: {e}")
    else:
        print("Failed to read localizations file.")


if __name__ == "__main__":
    main()
