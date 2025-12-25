# **ParseAI User Guide**

This guide provides a comprehensive overview of how to use ParseAI to turn your Google AI Studio exports into usable code repositories.

## **1. The Workflow**

1.  **Export**: Download your chat history as a JSON file from Google AI Studio.
2.  **Ingest**: Place the `.json` file into the `ingest/` directory in the ParseAI root.
3.  **Run**: Execute the `run_parser.sh` script.
4.  **Result**: Find your structured project in `output/<SessionName>/`.

## **2. Basic Usage**

The simplest way to run ParseAI is with default settings. This will parse all JSON files in `ingest/` and extract code blocks into a flat structure.

```bash
./parser_ai/run_parser.sh
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
./parser_ai/run_parser.sh -n
```

### **`--strip` / `-s`**
**Purpose**: Clean naming conventions.
**Behavior**: Removes specific prefixes from filenames using Regex. Can be used multiple times.
**Use Case**: If your System Prompt forces the AI to name files `py_script.py` (to help it distinguish types), you can use this flag to clean them back to `script.py` on disk.

```bash
# Input: py_main.py -> Output: main.py
./parser_ai/run_parser.sh --strip "^py_"
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
./parser_ai/run_parser.sh --reconstruct
./parser_ai/run_parser.sh --reconstruct
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

./parser_ai/run_parser.sh --reconstruct --merge-to ./my_app
```

### **Output Structures**
*   **`files/`**: **Flattened History**. Checks explicit paths (`src/utils.py`) and converts them to safe filenames (`src_utils.py`) to keep a flat list.
*   **`reconstructed/`**: **Path-Aware Structure**.
    *   Respects explicit paths defined in code fences (e.g., `src/core/main.py`).
    *   Creates the necessary directory tree automatically.
*   **`merged_project/`**: **Final Project**.
    *   Consolidated view of the `reconstructed/` folder.
    *   Contains the *latest version* of every file.

## **4. Advanced Combinations**

You can mix and match flags for powerful workflows.

**Example: The "Full Project" Run**
This command numbers every file (so no code is lost), strips the "py_" helper prefix, and reconstructs the folder structure.

```bash
```bash
./parser_ai/run_parser.sh -n -s "^py_" -s "^sh_" -r --merge-to ./full_project
```

**Result:**
**Result:**
*   `files/001_main.py`
*   `reconstructed/001_src/backend/main.py`
*   `merged_project/src/backend/main.py` (Created by `--clean-project`)
