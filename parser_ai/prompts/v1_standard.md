Project Structure and File Management

1. File Creation: Create files when necessary. Path files logically using the structure below.

2. Project Directory Structure (Recommended)
   * Initialization (Root): README, requirements.txt
   * Logic:
      * src/: Source code.
      * scripts/: Automation scripts.
   * Resources:
      * config/: Configuration files.
      * assets/: Images/Data.
   * Documentation:
      * docs/: Documentation.
      * tests/: Tests.

3. File Naming
   * Use static filenames for code (e.g. `main.py`).
   * Use descriptive names (e.g. `data_loader.py` instead of `script.py`).

4. Artifact Generation (Crucial)
   * **You MUST specify the full relative path** in the code block label.
   
   **Format:**
   ```language:path/to/filename.ext
   # Code content...
   ```
   
   **Examples:**
   * ` ```python:src/main.py `
   * ` ```json:config/settings.json `
