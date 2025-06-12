# /// script
# name = "gemini-json-ocr"
# readme = "README.md"
# requires-python = ">=3.12.0"
# dependencies = [
#     "python-dotenv",
#     "google-genai",
# ]
# [dependency-groups]
# dev = [
#     "ruff"
# ]
# ///
import argparse
import logging
import mimetypes
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

log_level = logging.DEBUG if os.getenv("DEBUG") else logging.INFO
logging.basicConfig(level=log_level)


def read_prompt_from_file(file_path: Path) -> str:
    if file_path is None:
        print("Error: No prompt provided.")
        sys.exit(1)

    if file_path.is_file():
        with open(file_path, encoding="utf-8") as pf:
            return pf.read().strip()
    else:
        print(f"Error: Prompt '{file_path}' not found or is not a file.")
        sys.exit(1)


def get_prompt(args) -> str:
    # TODO: It would be nice to support custom args, stdin etc.
    default_prompt_path = Path(__file__).parent / "prompt.txt"
    return read_prompt_from_file(default_prompt_path)


def process_with_gemini(path: str, client: genai.Client, prompt: str) -> str:
    logging.debug(f"Processing with Gemini: {path}")

    with open(path, "rb") as f:
        file_bytes = f.read()

    # Detect MIME type
    mime_type, _ = mimetypes.guess_type(path)
    if mime_type is None:
        # fallback if not detected
        mime_type = "application/pdf"

    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp"),
        contents=[
            prompt,
            genai.types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
        ],
        config=genai.types.GenerateContentConfig(response_mime_type="application/json"),
    )

    logging.debug(f"Received response from Gemini model: {response.text}")
    return response.text


def process_pdf_file(path: str, client: genai.Client, prompt: str, overwrite: bool, exit_on_skip: bool = False) -> bool:
    """
    Process a single PDF file.
    
    Args:
        path: Path to the PDF file
        client: Gemini client instance
        prompt: Prompt to use for Gemini
        overwrite: Whether to overwrite existing output files
        exit_on_skip: Whether to exit the program if file is skipped
        
    Returns:
        bool: True if processing was successful, False otherwise
    """
    if not os.path.isfile(path):
        print(f"Error: File '{path}' not found or is not a file.")
        if exit_on_skip:
            sys.exit(1)
        return False
        
    if not path.lower().endswith('.pdf'):
        print(f"Error: File '{path}' is not a PDF file.")
        if exit_on_skip:
            sys.exit(1)
        return False
        
    output_path = f"{path}.json"
    
    # If overwrite not set and output file exists, skip
    if not overwrite and os.path.exists(output_path):
        logging.info(
            f"Skipping {os.path.basename(path)} as {output_path} already exists. Use --overwrite to overwrite."
        )
        if exit_on_skip:
            sys.exit(0)
        return False
        
    try:
        logging.info(f"Processing file: {os.path.basename(path)}")
        results_json = process_with_gemini(path, client, prompt)

        # Write the output to {path}.json
        with open(output_path, "w", encoding="utf-8") as out_file:
            out_file.write(results_json)

        print(
            f"Results for {os.path.basename(path)} have been written to {output_path}\n"
        )
        return True
    except Exception as e:
        logging.error(f"Error processing {os.path.basename(path)}: {e}")
        if exit_on_skip:
            sys.exit(1)
        return False


def main():
    parser = argparse.ArgumentParser(description="Process PDF files using Gemini")
    
    # Create a mutually exclusive group for directory vs. file options
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "directory", nargs="?", help="Path to directory containing PDFs"
    )
    group.add_argument(
        "--directory", dest="directory_opt", help="Path to directory containing PDFs"
    )
    group.add_argument(
        "--file", dest="file_path", help="Path to a single PDF file to process"
    )
    
    parser.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing JSON files"
    )

    args = parser.parse_args()

    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key or google_api_key == "YOUR_API_KEY":
        print("Error: GOOGLE_API_KEY environment variable is not set.")
        sys.exit(1)

    prompt = get_prompt(args)
    client = genai.Client(api_key=google_api_key)

    # Process a single file
    if args.file_path:
        process_pdf_file(args.file_path, client, prompt, args.overwrite, exit_on_skip=True)
    else:
        # Process all files in a directory (existing functionality)
        directory = args.directory_opt if args.directory_opt else args.directory
        if not directory:
            print("Error: No directory specified.")
            sys.exit(1)

        if not os.path.isdir(directory):
            print(f"Directory '{directory}' not found or is not a directory")
            sys.exit(1)

        found_pdf = False
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.lower().endswith(".pdf"):
                    found_pdf = True  # Mark that we found a PDF file
                    path = os.path.join(directory, entry.name)
                    process_pdf_file(path, client, prompt, args.overwrite)

        if not found_pdf:
            print(f"No PDF files found in directory '{directory}'")
            sys.exit(1)


if __name__ == "__main__":
    main()
