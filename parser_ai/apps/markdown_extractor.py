import os
import sys
import argparse
from extractor import CodeExtractor

def main():
    parser = argparse.ArgumentParser(description="Extract code blocks from a Markdown file.")
    parser.add_argument("input_file", help="Path to the input Markdown file.")
    parser.add_argument("--parse", action='append', help="Custom regex pattern for filename detection. Capture group 1 must be the filename.", default=[])
    parser.add_argument("--add-numbering", "-n", action='store_true', help="Prepend sequential numbers to extracted filenames (e.g. 001_file.py).")
    parser.add_argument("--strip", "-s", action='append', help="Regex pattern to strip from start of filenames (e.g. '^py_').", default=[])
    parser.add_argument("--reconstruct", "-r", action='store_true', help="Reconstruct directory structure from flat filenames (e.g. src_main.py -> src/main.py).")
    args, unknown = parser.parse_known_args()

    input_path = os.path.abspath(args.input_file)
    
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    # Determine output directory (same as input file's directory)
    output_dir = os.path.dirname(input_path)
    filename = os.path.basename(input_path)

    print(f"Extracting code from: {filename}")
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()

        extractor = CodeExtractor(output_dir)
        num_files = extractor.extract_from_text(
            text, 
            filename, 
            custom_patterns=args.parse,
            add_numbering=args.add_numbering,
            strip_patterns=args.strip,
            reconstruct=args.reconstruct
        )
        
        if num_files > 0:
            print(f"  -> Extracted {num_files} files.")
        else:
            print("  -> No files found to extract.")

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
