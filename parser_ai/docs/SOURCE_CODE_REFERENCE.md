# **ParseAI Source Code Reference**

This document serves as a "Direct Report" on the internal logic of the ParseAI codebase. It explains *how* the code works, file by file.

## **1. Core Entry Point: `run_parser.sh`**
**Location**: `parser_ai/run_parser.sh`

This Bash script acts as the orchestrator for the entire pipeline.
*   **Environment Setup**: Resolves the project root and sets `PYTHONPATH` to ensure Python imports work correctly.
*   **Argument Parsing**: Pre-scans arguments to identify the output directory but passes `"$@"` (all arguments) directly to the Python scripts.
*   **Phase 1 (JSON Parsing)**: Calls `json_parser.py` to convert raw JSON logs into Markdown.
*   **Phase 2 (Extraction)**: Iterates through all generated `.md` files in the output directory and calls `markdown_extractor.py` for each one.
    *   *Note*: It only attempts extraction if Phase 1 exits successfully (Exit Code 0).

## **2. The Log Converter: `json_parser.py`**
**Location**: `parser_ai/apps/json_parser.py`

Responsible for ingesting Google AI Studio JSON exports and rendering them as human-readable Markdown.
*   **Input**: Scans the `ingest/` directory for `.json` files.
*   **Validation**: Checks (via heuristics) if a file is valid JSON before attempting to parse.
*   **Parsing Logic**:
    *   Reads `chunkedPrompt.chunks`.
    *   **Role Mapping**: Converts 'model' -> '🤖 AI', 'user' -> '👤 User'.
    *   **Thought Handling**: Detects `isThought: true` and formats these blocks as Markdown blockquotes (`> **THOUGHT**`) to distinguish internal reasoning from actual output.
*   **Output**: Writes a sanitized `.md` file to `output/<SessionName>/`.

## **3. The Bridge: `markdown_extractor.py`**
**Location**: `parser_ai/apps/markdown_extractor.py`

A CLI wrapper around the core extraction logic.
*   **Purpose**: Decouples the "files-on-disk" operations from the regex logic.
*   **Argument Handling**: Uses `argparse` to define flags like `--strip`, `--add-numbering`, and `--reconstruct`.
*   **Execution**: Validates input file existence, instantiates `CodeExtractor`, and prints a summary of extracted files.

## **4. The Engine: `extractor.py`**
**Location**: `parser_ai/apps/extractor.py`

This class (`CodeExtractor`) contains the intelligence for identifying, naming, and saving code files.

### **A. Detection (The "Event" Loop)**
The extractor scans the markdown text linearly and builds a list of "Events" (Headers or Code Blocks).
1.  **Headers**: Regex looks for `### File: name` or `Save as: name`.
2.  **Code Blocks**: Regex finds ` ```lang ... ``` ` blocks.
3.  **Inline Names**: It also detects "Tiny Blocks" (single lines inside backticks) which act as filenames for the *next* block if no explicit header exists.

### **B. Naming Strategy**
When a code block is ready to be saved, the extractor determines its filename in this priority:
1.  **Inline Fence Name**: ` ```python:src/main.py ` (Highest Priority - The "Golden Standard").
2.  **Tiny Block**: A preceding small code block containing just a filename.
3.  **Header**: A preceding `### File: ...` header.

### **C. Processing Pipeline (The `reconstruct` Logic)**
Once a filename is determined, it goes through a transformation pipeline before writing:
1.  **Sanitization**: Removes illegal OS characters (`:`, `*`, `?`, etc.).
2.  **Stripping**: Removes user-defined regex prefixes (e.g., removing `py_`).
3.  **Numbering (Prefix)**: If `-n` is on, a counter (`001_`) is prepared.

### **D. Dual Output System**
If the `--reconstruct` flag is active, the extractor writes to **two** locations:
1.  **`files/` (Flat)**: The filename is flattened (directories become ignored or part of the name). Uses `_save_content_safely` to handle version rotation (renaming collisions to `_v1`).
2.  **`reconstructed/` (Nested)**: The filename is split by underscores (`_`) to form a directory path (e.g., `src_main.py` -> `src/main.py`). Use `_save_content_safely` here as well to ensure parent directories exist.

### **E. Safety Mechanisms**
*   **Ghost Prevention**: It checks if `dest_path` exists. If so, it "rotates" the old file (renames it to `_vX`) before writing the new one.
*   **Directory Validation**: Always ensures `os.makedirs(parent_dir)` is called before opening a file for writing.
