# **ParseAI: The Prompting Protocol**

To guarantee perfect extraction and project reconstruction, you must align the LLM's output with ParseAI's "Explicit Path" logic. This guide provides the final, canonical **System Prompt**.

## **The Core Philosophy: "Explicit Paths"**

ParseAI is now **Path-Aware**. It does not guess your directory structure; it respects what the LLM explicitly tells it.

*   **Old Way (Legacy)**: `py_src_main.py` (Too ambiguous, relies on splitting)
*   **New Way (Protocol)**: `src/main.py` (Explicit, unambiguous, standard)

When the LLM outputs a code fenced with `python:src/backend/server.py`, ParseAI knows exactly where to put it.

---

## **The "God Mode" System Prompt**

Copy and paste this block into your Custom Instructions or System Prompt. It forces the LLM to output files in the exact format ParseAI expects.

```markdown
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
```

---

## **How ParseAI Reacts**

1.  **You Prompt**: "Update the server configuration."
2.  **LLM Generates**:
    *   ` ```json:config/server.json `
3.  **You Run**: 
    ```bash
    ./parseAI/run_parser.sh --reconstruct
    ```
4.  **ParseAI Delivers**:
    *   `reconstructed/config/server.json` (Exact structure preserved)
    *   `files/config_server.json` (Flattened backup for history)

## **Tips for Success**

*   **Always use `--reconstruct`**: This enables the path-aware logic.
*   **Always use `--clean-project`**: This automatically merges your reconstructed files into a clean `merged_project/` folder, giving you a ready-to-run project.