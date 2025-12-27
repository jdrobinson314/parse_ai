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
    parser.add_argument("--merge-to", "-m", help="Merge reconstructed files into a single unified directory (e.g. ./my_project). Overwrites older versions.")
    parser.add_argument("--clean-project", "-cp", action='store_true', help="Automatically reconstructs and merges files into a 'merged_project' folder inside the session directory. (Shortcut for -r and -m)")
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
            reconstruct=args.reconstruct or args.clean_project
        )
        
        if num_files > 0:
            print(f"  -> Extracted {num_files} files.")
            
            # Determine Merge Target
            merge_target = args.merge_to
            if args.clean_project:
                # Default "clean project" location: inside the extraction folder
                # output_dir is where the JSON parsing put the MD file? No, it's where we WANT output.
                # Actually, extractor uses output_dir + f"{source_name}_files"
                source_name = os.path.splitext(filename)[0]
                base_files_dir = os.path.join(output_dir, f"{source_name}_files")
                merge_target = os.path.join(base_files_dir, "merged_project")

            # Perform Merge if Requested
            if merge_target:
                source_name = os.path.splitext(filename)[0]
                manifest_path = os.path.join(output_dir, f"{source_name}_files", "manifest.json")
                
                extractor.merge_reconstruction(
                    manifest_path, 
                    merge_target, 
                    clean_target=args.clean_project
                )

        else:
            print("  -> No files found to extract.")

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
