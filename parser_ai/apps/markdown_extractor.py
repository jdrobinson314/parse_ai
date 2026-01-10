import os
import sys
import argparse
import json
from extractor import CodeExtractor
from html_generator import generate_html_from_markdown
from pdf_generator import generate_pdf

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

def prettify_title(filename):
    """
    Converts a filename like 'project_docs_readme.md' into 'Project Docs - Readme'.
    """
    base = os.path.splitext(filename)[0]
    # Replace common separators with spaces
    clean = base.replace('_', ' ').replace('-', ' ')
    # Title Case
    clean = clean.title()
    return clean

def parse_custom_header(text, border_char="-"):
    """
    Parses the top of the file for a custom header block ending with a line of border_chars.
    Returns: (header_html, body_text)
    """
    lines = text.split('\n')
    header_lines = []
    border_found = False
    stop_idx = 0
    
    # Heuristic: Scan top 20 lines
    for i, line in enumerate(lines[:20]):
        stripped = line.strip()
        # Check if line is a border line (e.g. "---", "# ---", "// ---")
        # We check if it contains at least 3 border chars and mostly border chars (ignoring comment markers)
        path_chars = stripped.replace(' ', '').replace('#', '').replace('/', '').replace('*', '')
        
        if len(path_chars) >= 3 and all(c == border_char for c in path_chars):
             border_found = True
             stop_idx = i + 1
             break
        header_lines.append(line)
        
    if border_found:
        # Construct header HTML
        # We strip comment characters for cleaner display?
        # User said "appear as a code block". We can just preserve it raw.
        # But we might want to color it.
        # Let's return the raw lines to be put in the code block.
        raw_header = "\n".join(header_lines)
        body_text = "\n".join(lines[stop_idx:]).lstrip()
        return raw_header, body_text
        
    return None, text

def process_markdown_file(input_path, args, processed_set=None):
    """
    Recursively extracts code from a markdown file and processes nested markdown files.
    """
    if processed_set is None:
        processed_set = set()
    
    # Avoid infinite recursion
    abs_path = os.path.abspath(input_path)
    if abs_path in processed_set:
        print(f"Skipping already processed file: {input_path}")
        return
    processed_set.add(abs_path)
    
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}")
        return

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
            print(f"  -> Extracted {num_files} files from {filename}.")
            
            # Helper to get the extraction directory (output_dir/[filename]_files)
            source_name = os.path.splitext(filename)[0]
            base_extraction_dir = os.path.join(output_dir, f"{source_name}_files")
            
            # Process Manifest for Recursive Extraction
            manifest_path = os.path.join(base_extraction_dir, "manifest.json")
            
            # --- MERGE LOGIC REMOVED FOR SIMPLICITY RECURSION, or keep it? ---
            # Keeping merge logic for the top-level or sub-levels if requested.
            # Determine Merge Target
            merge_target = args.merge_to
            if args.clean_project:
                merge_target = os.path.join(base_extraction_dir, "merged_project")

            if merge_target:
                extractor.merge_reconstruction(
                    manifest_path, 
                    merge_target, 
                    clean_target=args.clean_project
                )
            
            # --- RECURSIVE STEP ---
            if os.path.exists(manifest_path):
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                
                for entry in manifest:
                    # Determine where the file is on disk
                    # It could be in 'saved_as' (files/) or 'reconstructed_path' (reconstructed/)
                    # We usually want to process the one in 'files/' as the "master" reference? 
                    # OR if reconstructed exists, use that?
                    # Let's prioritize 'saved_as' as it is the flat/standard output.
                    
                    target_rel_path = entry.get('saved_as')
                    if not target_rel_path and 'reconstructed_path' in entry:
                         # Fallback to reconstructed path if 'files' logic failed?
                         # Usually both exist if Reconstruct is ON. 
                         # Extractor always writes to 'files/', 'reconstructed/' is optional.
                         pass
                    
                    if target_rel_path:
                        # Full path to extracted file
                        extracted_file_path = os.path.join(base_extraction_dir, "files", target_rel_path)
                        
                        # Check extension
                        if extracted_file_path.lower().endswith('.md'):
                            print(f"  [Recursive] Found Markdown file: {target_rel_path}")
                            
                            # 1. Generate HTML/PDF for this sub-file
                            file_base = os.path.splitext(extracted_file_path)[0]
                            html_path = f"{file_base}.html"
                            pdf_path = f"{file_base}.pdf"
                            
                            try:
                                with open(extracted_file_path, 'r', encoding='utf-8') as mf:
                                    md_content = mf.read()
                                
                                # Generate Friendly Title
                                pretty_title = prettify_title(target_rel_path)
                                
                                # Parse Custom Header from Content
                                custom_header, body_content = parse_custom_header(md_content, border_char=args.header_border_char)
                                
                                # Logic: If custom header found, use IT as the subtitle/block content relative to the pretty title.
                                # OR replace the subtitle logic entirely.
                                # User wanted "investigate subsequent header lines... appear as a code block".
                                # If custom header exists, we pass it as 'header_block' content?
                                # We need to update HTML generator signature one more time or abuse 'subtitle'.
                                # I will pass it as 'subtitle' but wrap it uniquely so HTML generator knows not to just text-node it?
                                # Actually, HTML gen takes 'subtitle' and puts it in .file-path (div).
                                # If I pass the raw header lines with newlines, I should wrap them in <pre>.
                                
                                final_subtitle = target_rel_path
                                if custom_header:
                                    # Format the header lines for the block
                                    # Escape HTML
                                    import html
                                    safe_header = html.escape(custom_header)
                                    final_subtitle = f"{target_rel_path}<hr style='border:0; border-top:1px solid #555; margin:5px 0;'><pre style='background:none; border:none; padding:0; margin:0; color:#ddd;'>{safe_header}</pre>"
                                
                                # Generate HTML
                                if generate_html_from_markdown(body_content, html_path, title=pretty_title, subtitle=final_subtitle):
                                    # Generate PDF
                                    # We don't have page_size in args for this script... assume Letter?
                                    # Or add it to args.
                                    generate_pdf(html_path, pdf_path, page_size="Letter")
                            except Exception as e:
                                print(f"  [Recursive] Failed to generate docs for {target_rel_path}: {e}")

                            # 2. Recurse!
                            # Pass 'args' down.
                            process_markdown_file(extracted_file_path, args, processed_set)

        else:
            print(f"  -> No files found to extract in {filename}.")

    except Exception as e:
        print(f"An error occurred processing {filename}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Extract code blocks from a Markdown file.")
    parser.add_argument("input_file", help="Path to the input Markdown file.")
    parser.add_argument("--parse", action='append', help="Custom regex pattern for filename detection. Capture group 1 must be the filename.", default=[])
    parser.add_argument("--add-numbering", "-n", action='store_true', help="Prepend sequential numbers to extracted filenames (e.g. 001_file.py).")
    parser.add_argument("--strip", "-s", action='append', help="Regex pattern to strip from start of filenames (e.g. '^py_').", default=[])
    parser.add_argument("--reconstruct", "-r", action='store_true', help="Reconstruct directory structure from flat filenames (e.g. src_main.py -> src/main.py).")
    parser.add_argument("--merge-to", "-m", help="Merge reconstructed files into a single unified directory (e.g. ./my_project). Overwrites older versions.")
    parser.add_argument("--clean-project", "-cp", action='store_true', help="Automatically reconstructs and merges files into a 'merged_project' folder inside the session directory. (Shortcut for -r and -m)")
    parser.add_argument("--header-border-char", default="-", help="Character that defines the end of the header block (repeated). Default is '-'.")
    args, unknown = parser.parse_known_args()

    input_path = os.path.abspath(args.input_file)
    
    # Start recursive processing
    process_markdown_file(input_path, args)

if __name__ == "__main__":
    main()
