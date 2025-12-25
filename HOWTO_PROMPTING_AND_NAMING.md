### SYSTEM PROTOCOL: FILE ORGANIZATION & GENERATION

**1. DIRECTORY STRUCTURE & PATHS**
Sort generated content into the following logic-based directories (create new paths only if necessary):
* `src/`     : Main application source code (Python).
* `scripts/` : Shell/Bash execution wrappers or maintenance scripts.
* `config/`  : Static configuration files (JSON, YAML, INI).
* `docs/`    : Text files, logs, and markdown documentation.
* `data/`    : Binary definitions or raw data schemas.

**2. NAMING CONVENTION (Clean Syntax)**
* **A. SOURCE & CONFIG (`.py`, `.sh`, `.json`, `.yaml`)**
    * *Rule:* Use static filenames to ensure imports/paths remain stable.
    * *Format:* `{PROJECT}_{DESCRIPTOR}.{EXT}`
    * *Example:* `aiwye_loader.py` (NOT `py_aiwye_loader.py`)
    * *Versioning:* Stored internally in the **Header**.

* **B. TEXT & LOGS (`.txt`, `.md`)**
    * *Rule:* These are historical artifacts.
    * *Format:* `{PROJECT}_{DESCRIPTOR}_v{VERSION}.{EXT}`
    * *Example:* `aiwye_changelog_v04.txt`
    * *Versioning:* Stored in the **Filename**.

**3. CODE BLOCK FORMATTING (Path-Aware)**
Code blocks must indicate the **full relative path** in the fence label.
* *Format:* ` ```language:path/to/filename `
* *Example:* ` ```python:src/aiwye_core.py `
* *Example:* ` ```bash:scripts/start_server.sh `

**4. SHEBANG & HEADERS**
All executable files must start with the appropriate Linux interpreter and a uniform metadata block.

* **Python Files:**
    ```python
    #!/usr/bin/env python3
    # ------------------------------------------------------------------
    # FILE:     src/{filename}
    # VERSION:  v{XX}
    # CONTEXT:  Linux (Python 3)
    # ------------------------------------------------------------------
    ```

* **Bash/Shell Files:**
    ```bash
    #!/bin/bash
    # ------------------------------------------------------------------
    # FILE:     scripts/{filename}
    # VERSION:  v{XX}
    # ------------------------------------------------------------------
    ```