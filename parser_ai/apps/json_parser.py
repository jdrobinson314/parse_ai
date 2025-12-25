import json
import os
import sys
import re
import argparse

# Configuration
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_INGEST_DIR = os.path.join(PROJECT_ROOT, "ingest")
DEFAULT_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

ROLE_MAP = {
    "model": "🤖 AI",
    "user": "👤 User",
    "system": "⚙️ System"
}

def extract_metadata(data):
    """Extracts run settings and other metadata."""
    metadata = []
    run_settings = data.get("runSettings", {})
    
    if "model" in run_settings:
        metadata.append(f"Model: {run_settings['model']}")
    if "temperature" in run_settings:
        metadata.append(f"Temperature: {run_settings['temperature']}")
    
    if metadata:
        return "--- Metadata ---\n" + "\n".join(metadata) + "\n----------------\n\n"
    return ""

def format_role(role_key):
    """Maps raw role keys to display names."""
    return ROLE_MAP.get(role_key, role_key.title())

def parse_file(file_path):
    """
    Parses a single JSON file and extracts conversation text with enhanced formatting.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check for expected structure
        if 'chunkedPrompt' not in data or 'chunks' not in data['chunkedPrompt']:
            print(f"Skipping {file_path}: 'chunkedPrompt.chunks' not found.")
            return

        output_content = []
        
        # 1. Metadata
        output_content.append(extract_metadata(data))

        chunks = data['chunkedPrompt']['chunks']
        separator = "\n\n---\n\n"

        for chunk in chunks:
            role_key = chunk.get('role', 'unknown')
            text = chunk.get('text', '')
            is_thought = chunk.get('isThought', False)
            
            display_role = format_role(role_key)
            
            if is_thought:
                # 2. Thought Handling - Markdown blockquote
                # Indent all lines with > to make it a proper blockquote
                quoted_text = text.replace('\n', '\n> ')
                formatted_chunk = f"> **THOUGHT** ({display_role}):\n> {quoted_text}\n"
            else:
                # 3. Standard Turn - Markdown Header
                formatted_chunk = f"## {display_role}\n\n{text}\n"
            
            output_content.append(formatted_chunk)
            output_content.append(separator)

        return "".join(output_content)

    except json.JSONDecodeError:
        print(f"Error decoding JSON from {file_path}")
    except Exception as e:
        print(f"Unexpected error processing {file_path}: {e}")
    return None

def main():
    parser = argparse.ArgumentParser(description="Parse JSON conversation logs to Markdown.")
    parser.add_argument("--input", "-i", default=DEFAULT_INGEST_DIR, help="Directory containing JSON files")
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT_DIR, help="Directory to save output Markdown files")
    
    # We use parse_known_args because run_parser.sh passes "$@" which might contain other args (though currently it doesn't)
    args, unknown = parser.parse_known_args()

    input_dir = os.path.abspath(args.input)
    output_dir = os.path.abspath(args.output)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # List files in ingest directory
    if not os.path.exists(input_dir):
        print(f"Input directory not found: {input_dir}")
        return

    all_files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f)) and not f.startswith('.')]
    json_files = []

    for f in all_files:
        path = os.path.join(input_dir, f)
        if f.endswith('.json'):
            json_files.append(f)
        elif '.' not in f:
            # Check if "un-affixed" file is valid JSON
            try:
                with open(path, 'r', encoding='utf-8') as tf:
                    # Read first char as quick check
                    first_char = tf.read(1)
                    if first_char not in ('{', '['):
                        continue
                    # Try full load
                    tf.seek(0)
                    data = json.load(tf)
                    # Optional: Check for our specific schema keys to be even surer?
                    # For now, valid JSON is enough to try parsing.
                    json_files.append(f)
            except Exception:
                # Not a JSON file, silently skip
                continue
    
    if not json_files:
        print(f"No JSON files found in {input_dir}")
        return

    print(f"Found {len(json_files)} valid JSON files in {input_dir}. Outputting to: {output_dir}")

    for filename in json_files:
        file_path = os.path.join(input_dir, filename)
        print(f"Processing: {filename}")
        
        extracted_text = parse_file(file_path)
        
        if extracted_text:
            # Sanitize and format output filename
            base_name = os.path.splitext(filename)[0]
            # Remove invalid chars
            safe_name = re.sub(r'[<>:"/\\|?*]', '', base_name)
            # Collapse whitespace
            safe_name = re.sub(r'\s+', '_', safe_name).strip()
            
            output_filename = f"{safe_name}.md"
            
            # Create a dedicated directory for this run
            run_output_dir = os.path.join(output_dir, safe_name)
            if not os.path.exists(run_output_dir):
                os.makedirs(run_output_dir)

            output_path = os.path.join(run_output_dir, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(extracted_text)
            
            print(f"Saved output to: {output_path}")

            # 4. Extract and Save "System Instructions" (Sidecar)
            system_instruction = data.get("systemInstruction", {}).get("text")
            if system_instruction:
                sys_filename = f"{safe_name}_system_prompt.txt"
                sys_path = os.path.join(run_output_dir, sys_filename)
                with open(sys_path, 'w', encoding='utf-8') as f:
                    f.write(system_instruction)
                print(f"Saved System Instructions to: {sys_path}")

if __name__ == "__main__":
    main()
