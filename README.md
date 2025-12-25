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
- Output text files to `parser_ai/output/`.
- Extract code files to subdirectories in `parser_ai/output/`.

### Command Line Options

```bash
./parser_ai/run_parser.sh --help
```

## Features

### 1. Conversational Parsing
Converts raw JSON logs into a human-readable chat format.
- Handles standard user/model turns.
- Separates "thought" blocks from the final response.
- Extracts run metadata (model, temperature, etc.).

### 2. Automatic Code Extraction
The parser looks for specific patterns in the AI's response to identify and extract files.

**Supported Patterns:**

1. **Header Association:**
   ```text
   ### File <N>: <filename>
   **Description:** <description>
   ```
   *Followed by a code block.*

2. **Inline Filename:**
   ```markdown
   ```python: my_script.py
   print("Hello World")
   ```
   ```

3. **Custom CLI Pattern:**
   You can define your own regex pattern via the CLI:
   ```bash
   python apps/markdown_extractor.py input.md --parse "MyFile: (.+)"
   ```

**Extraction Logic:**
1.  Creates a subdirectory named after the source file (e.g., `MyLog_files/`).
2.  Saves the code block to the detected filename.
3.  Preference is given to inline filenames (inside the code fence) over header-based filenames.
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
```
