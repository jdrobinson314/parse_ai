# **ParseAI User Guide**

This guide provides a comprehensive overview of how to use ParseAI to turn your Google AI Studio exports into usable code repositories.

## **1. The Workflow**

1.  **Export**: Download your chat history as a JSON file from Google AI Studio.
2.  **Ingest**: Place the `.json` file into the `ingest/` directory in the ParseAI root.
3.  **Run**: Execute the `run_parser.sh` script.
4.  **Result**: Find your structured project in `output/<SessionName>/`.

## **2. Basic Usage**

The simplest way to run ParseAI is with default settings. This will parse all `.json` files in `ingest/`.
- Converts chat logs to **Markdown**, **HTML**, and **PDF**.
- Extracts code blocks into a structured folder system.
- Recursively processes any Markdown files extracted from the chat.

```bash
# Linux / MacOS
./parseAI/run_parser.sh

# Windows
.\parseAI\run_parser.ps1
```

## **3. Command Line Arguments**

ParseAI offers several flags to control how files are named and organized.

### **`--help` / `-h`**
Displays the help menu with a list of available arguments.

### **`--add-numbering` / `-n`**
**Purpose**: Preservation of history.
**Behavior**: Prepends a sequential 3-digit number to every extracted file (e.g., `001_main.py`, `002_main.py`).
**Use Case**: Essential when the AI rewrites the same file multiple times in one conversation. This ensures you save *every* version rather than just the last one.

```bash
# Result: 001_script.py, 002_script.py
./parseAI/run_parser.sh -n
```

### **`--strip` / `-s`**
**Purpose**: Clean naming conventions.
**Behavior**: Removes specific prefixes from filenames using Regex. Can be used multiple times.
**Use Case**: If your System Prompt forces the AI to name files `py_script.py` (to help it distinguish types), you can use this flag to clean them back to `script.py` on disk.

```bash
# Input: py_main.py -> Output: main.py
./parseAI/run_parser.sh --strip "^py_"
```

### **`--reconstruct` / `-r`**
**Purpose**: Directory Structure Recovery.
**Behavior**: Converts underscores in filenames into directory separators.
**Safety**: Automatically creates parent directories if they don't exist.
**Dual Output**: When used, this produces **two** output paths for safety and convenience:
1.  `files/`: The "Flat Archive" (e.g., `src_backend_server.py`). Always safe, no overwrites due to folder naming collisions.
2.  `reconstructed/`: The "Nested Project" (e.g., `src/backend/server.py`).

```bash
# Input: src_utils_logger.py
# Output: reconstructed/src/utils/logger.py
./parseAI/run_parser.sh --reconstruct
./parseAI/run_parser.sh --reconstruct
```

### **`--merge-to` / `-m`**
**Purpose**: Unified Project Creation.
**Behavior**: Consolidates the fragmented, time-stamped directories created by reconstruction into a single, clean project structure (e.g. `./my_new_app`).
**Strategy**: Uses a "Last-Write-Wins" policy. If `main.py` was created 3 times in the chat, the final project will contain the content of the 3rd version.

```bash
# Input: 
#   - 001_src_main.py (Old)
#   - 003_src_main.py (New)
# Output: 
#   - ./my_app/src/main.py (New Content)

./parseAI/run_parser.sh --reconstruct --merge-to ./my_app
```

### **Output Structures**
*   **`files/`**: **Flattened History**. Checks explicit paths (`src/utils.py`) and converts them to safe filenames (`src_utils.py`) to keep a flat list.
*   **`reconstructed/`**: **Path-Aware Structure**.
    *   Respects explicit paths defined in code fences (e.g., `src/core/main.py`).
    *   Creates the necessary directory tree automatically.
*   **`merged_project/`**: **Final Project**.
    *   Consolidated view of the `reconstructed/` folder.
    *   Consolidated view of the `reconstructed/` folder.
    *   Contains the *latest version* of every file.

### **`--clean-project` / `-cp`**
**Purpose**: One-Shot Project Build.
**Behavior**: Shortcut for `-r` and `-m`. Immediately reconstructs files and merges them into a `merged_project/` folder inside the `_files` output directory. 

### **`--page-size`**
**Purpose**: Output Formatting.
**Behavior**: Sets the page size for the generated PDF documentation.
**Default**: `Letter`
**Values**: `A4`, `Legal`, `Letter`, etc.

```bash
./parseAI/run_parser.sh --page-size A4
```

### **`--header-border-char`**
**Purpose**: Metadata Parsing.
**Behavior**: Defines the character used to identify the "Header Block" within extracted Markdown files.
**Default**: `-`
**Mechanism**: If a file starts with lines of text followed by a separator line (e.g., `-------`), the parser treats the top section as Metadata and styles it into a code block in the HTML/PDF.

```bash
# Parses headers ending with "======="
./parseAI/run_parser.sh --header-border-char "="
```

## **4. Advanced Custom Parsing (`--parse`)**

ParseAI allows you to inject custom parsing logic directly from the command line using the `--parse` argument. This is powerful when you are dealing with log files or chat exports that use different conventions for naming files.

**How it Works**: The parser accepts a Python Regular Expression. **Crucially, you must use a capture group `(...)` to indicate which part of the pattern is the filename.**

### Examples

**Scenario A: The "Save As" Pattern**
> Start of File: `Save this code as: server.js`
*   **Regex**: `Save this code as:\s*(.+)`
*   **Command**:
    ```bash
    ./parseAI/run_parser.sh --parse "Save this code as:\s*(.+)"
    ```

**Scenario B: The Bracket Style**
> Start of File: `[FILE] /src/components/Button.tsx`
*   **Regex**: `\[FILE\]\s+(.+)`
*   **Command**:
    ```bash
    ./parseAI/run_parser.sh --parse "\[FILE\]\s+(.+)"
    ```

    ./parseAI/run_parser.sh --parse "\[FILE\]\s+(.+)"
    ```

## **5. Recursive Processing**

If your chat log contains **Markdown files** (e.g., the AI generates a `README.md` or `design_doc.md`), ParseAI recursively treats them as mini-projects:
1.  **Documentation**: It automatically generates an HTML and PDF version of that extracted file.
2.  **Nested Extraction**: It scans the extracted markdown file for *more* code blocks or file definitions.
    *   If `doc.md` contains a Python script, that script will be extracted to `doc_files/files/script.py`.

## **6. Advanced Combinations**

You can mix and match flags for powerful workflows.

**Example: The "Full Project" Run**
This command numbers every file (so no code is lost), strips the "py_" helper prefix, and reconstructs the folder structure.

```bash
./parseAI/run_parser.sh -n -s "^py_" -s "^sh_" -r --merge-to ./full_project
```

**Result:**
*   `files/001_main.py`
*   `reconstructed/001_src/backend/main.py`
*   `merged_project/src/backend/main.py` (Created by `--merge-to`)
