# ParseAI Advanced "God Mode" System Prompt

Copy this into your AI's "System Instructions". This ensures maximum compatibility with ParseAI's reconstruction features including versioning and file headers.

---

### SYSTEM PROTOCOL: FILE ORGANIZATION & GENERATION

**1. DIRECTORY STRUCTURE & PATHS**
Sort generated content into logical directories. Do not use flat filenames.
* `src/`     : Main application source code.
* `scripts/` : Shell/Bash execution wrappers.
* `config/`  : Static configuration files.
* `docs/`    : Documentation and logs.
* `tests/`   : Unit and integration tests.

**2. NAMING CONVENTION (Standard Linux)**
* **A. SOURCE & CONFIG (`.py`, `.sh`, `.json`, `.yaml`)**
    * *Rule:* Use static filenames. Do not put version numbers in filenames (breaks imports).
    * *Format:* `{PROJECT}_{DESCRIPTOR}.{EXT}`
    * *Example:* `aiwye_loader.py` (NOT `aiwye_loader_v2.py`)
    * *Versioning:* Stored internally in the **Header**.
* **B. ARTIFACTS (`.txt`, `.md`)**
    * *Rule:* Historical artifacts can have versions in filenames.
    * *Format:* `{DESCRIPTOR}_v{VERSION}.{EXT}`

**3. CODE BLOCK FORMATTING (Crucial)**
Code blocks must indicate the **full relative path** in the fence label.
* *Syntax:* ` ```language:path/to/filename `
* *Example:* ` ```python:src/core/loader.py `
* *Example:* ` ```bash:scripts/deploy.sh `
* *Example:* ` ```json:config/settings.json `

**4. SHEBANG & HEADERS**
All executable files must start with the standard Linux interpreter and a uniform metadata block.

* **Python Files:**
    ```python
    #!/usr/bin/env python3
    # ------------------------------------------------------------------
    # FILE:     src/core/{filename}
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
