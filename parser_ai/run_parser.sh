#!/bin/bash

# ParseAI Launcher Script
# This script sets up the environment and runs the JSON parser.

# Resolve the directory of this script to find the project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/.."
APPS_DIR="$SCRIPT_DIR/apps"

# Ensure we are running with the correct python context
PYTHON_CMD="python3"

# Check if help is requested
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "========================================================"
    echo " ParseAI - JSON Parser & Code Extractor"
    echo "========================================================"
    echo "Usage: ./run_parser.sh [OPTIONS]"
    echo ""
    echo "Description:"
    echo "  Parses JSON conversation logs from the 'ingest' directory,"
    echo "  converts them to human-readable text, and extracts any"
    echo "  marked code files into separate directories."
    echo ""
    echo "Options:"
    echo "  --help, -h          Show this help message and exit."
    echo "  --add-numbering, -n Prepend sequential numbers to filenames."
    echo "  --strip, -s         Regex pattern to strip from filenames."
    echo "  --reconstruct, -r   Reconstruct directory structure from underscores."
    echo ""
    echo "Structure:"
    echo "  Input:  /home/jamesr/Development/AiDev/ParseAi/ingest/*.json"
    echo "  Output: /home/jamesr/Development/AiDev/ParseAi/output/"
    echo ""
    exit 0
fi

# Default Output Directory
DEFAULT_OUTPUT_DIR="$PROJECT_ROOT/output"
OUTPUT_DIR="$DEFAULT_OUTPUT_DIR"

# Pre-scan arguments to find --output or -o for the shell script's knowledge
# We don't consume them because we pass "$@" to the python script
args=("$@")
for ((i=0; i<${#args[@]}; i++)); do
    if [[ "${args[i]}" == "--output" || "${args[i]}" == "-o" ]]; then
        # Check if next argument exists
        if [[ -n "${args[i+1]}" ]]; then
            OUTPUT_DIR="${args[i+1]}"
            # Resolve absolute path if needed, though python script handles relative paths too.
            # But for shell 'find', relative path from where?
            # It's safer to resolve it relative to CWD if it's not absolute.
            if [[ "$OUTPUT_DIR" != /* ]]; then
                OUTPUT_DIR="$(pwd)/$OUTPUT_DIR"
            fi
        fi
    fi
done

echo "Starting ParseAI..."
echo "Project Root: $PROJECT_ROOT"
echo "Output Directory: $OUTPUT_DIR"

# We run from the apps directory or set PYTHONPATH to ensure imports work
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# 1. Run the JSON Parser (Converts JSON -> Markdown)
echo "Running JSON Parser..."
"$PYTHON_CMD" "$APPS_DIR/json_parser.py" "$@"
JSON_PARSER_EXIT_CODE=$?

if [ $JSON_PARSER_EXIT_CODE -ne 0 ]; then
    echo "ParseAI: JSON Parser failed (Exit Code: $JSON_PARSER_EXIT_CODE)."
    exit $JSON_PARSER_EXIT_CODE
fi

# 2. Run the Markdown Extractor (Extracts Code -> Files)
echo "Running Code Extraction..."

if [ -d "$OUTPUT_DIR" ]; then
    # Check if there are any .md files before looping to avoid "No such file or directory" errors
    # Use find to locate .md files recursively (handling spaces in filenames)
    while IFS= read -r md_file; do
        if [ -f "$md_file" ]; then
            echo "Extracting code from: $md_file"
            # Pass custom args to extractor if needed? The extractor mainly needs input file.
            # BUT, we might have --parse "pattern", which markdown_extractor DOES accept now.
            # so we should pass "$@" to markdown_extractor?
            # markdown_extractor expects: input_file [optional args]
            
            # Simple approach: We filter "$@" to only include --parse args? 
            # Or just pass "$@" and let argparse ignore unknown?
            # argparse defaults to error on unknown args unless parse_known_args is used.
            # markdown_extractor uses parse_args() which is strict.
            # We should probably fix markdown_extractor to be permissive OR filter args here.
            
            # For now, let's update markdown_extractor to use parse_known_args as well? 
            # Or simpler: Just extract the --parse args from "$@" here.
            
            # Better: Pass full "$@" to extractor, but update extractor to ignore -i/--input/--output.
            
             "$PYTHON_CMD" "$APPS_DIR/markdown_extractor.py" "$md_file" "${args[@]}"
            if [ $? -ne 0 ]; then
                echo "ParseAI: Markdown extractor failed for $md_file."
                # Decide whether to exit or continue on error for markdown extractor
                # For now, we'll just report and continue.
            fi
        fi
    done < <(find "$OUTPUT_DIR" -name "*.md")
    # shopt -u nullglob # Not needed with find
else
    echo "ParseAI: Output directory not found: $OUTPUT_DIR. Skipping markdown extraction."
fi

echo "ParseAI completed successfully."
exit 0
