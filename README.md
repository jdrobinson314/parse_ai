# ParseAI

ParseAI is a tool designed to process JSON conversation logs, converting them into readable text formats and automatically extracting code blocks into organized file structures.

## Overview

The core functionality involves:
1.  **Ingestion**: Reading JSON files from the `ingest/` directory.
2.  **Parsing**: Converting the JSON structure (roles, text, thoughts) into a readable format.
3.  **Extraction**: Scanning the parsed text for file definitions and extracting them to disk.

## Usage

### Quick Start

The easiest way to run ParseAI is using the launcher script:

```bash
./parser_ai/run_parser.sh
```

This will:
- Process all files in `ingest/`.
- Output text files to `output/`.
- Extract code files to subdirectories in `output/`.

### Command Line Options

```bash
./parser_ai/run_parser.sh --help
```

**Advanced Naming Options:**
*   `--add-numbering` / `-n`: Prepend sequential numbers (e.g. `001_script.py`) to keep files sorted chronologically.
*   `--strip "REGEX"` / `-s "REGEX"`: Remove unwanted prefixes from filenames. Can be used multiple times.
    *   Example: `--strip "^py_" --strip "^sh_"` transforms `py_main.py` -> `main.py`.

## Features

### 1. Conversational Parsing
Converts raw JSON logs into a human-readable chat format.
- Handles standard user/model turns.
- Separates "thought" blocks from the final response.
- Extracts run metadata (model, temperature, etc.).

### 2. Automatic Code Extraction
The parser looks for specific patterns in the AI's response to identify and extract files.

**Supported Patterns (Default):**

The parser uses a variety of strategies to detect filenames. It scans for:

1.  **Code Fence (The "Golden Standard")**:
    The most reliable method. Specify the filename directly in the language tag.
    ```markdown
    ```python: src/main.py
    print("code")
    ```
    ```

2.  **Explicit Headers**:
    ```text
    ### File 1: script.py
    ```

3.  **Natural Language Instructions**:
    *   `Save this as: utils.py`
    *   `File: config.json`
    *   `Filename: Dockerfile`
    *   `Create app.py` (Must have a file extension to be detected)

4.  **Tiny Block Heuristic**:
    If a code block is very short (<100 chars), has no spaces or newlines, and looks like a filename, it is treated as a file declaration for the *next* code block.
    ```markdown
    ```text
    path/to/file.js
    ```
    ```

5.  **Custom Patterns**:
    Define your own using the `--parse` argument.

**Extraction Logic:**
1.  Creates a subdirectory named after the source file (e.g., `MyLog_files/`).
2.  Saves the code block to the detected filename.
3.  **Precedence**: Inline filenames (Method 1) > Tiny Block (Method 4) > Header Association (Methods 2 & 3).
4.  Duplicate files are handled gracefully; header declarations without code blocks are ignored (no 0-byte ghost files).

## Documentation

*   [**Plugin Roadmap**](parser_ai/docs/PLUGIN_ROADMAP.md) - Future plans for extensibility.
*   [**Advanced Regex & Prompting Guide**](parser_ai/docs/REGEX_AND_PROMPTING_GUIDE.md) - **Read this!** How to control file naming with custom regex and System Prompts for Google AI Studio/ChatGPT.

## Directory Structure

```text
.
├── ingest/                  # Place your JSON logs here
├── parser_ai/
│   ├── apps/
│   │   ├── json_parser.py   # Main logic
│   │   └── extractor.py     # Code extraction module
│   ├── docs/                # Documentation
│   └── run_parser.sh        # Launcher script
├── output/                  # Generated files go here
└── README.md

## License

This project is licensed under the terms of the MIT License. See [LICENSE](LICENSE) for details.
\
© 2025 James D. Robinson, and Gemini
