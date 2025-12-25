# **ParseAI: The Prompting Protocol**

To get the most out of ParseAI, you need to align the LLM's output with the parser's logic. This guide provides a single, unified strategy for **"Chat-to-Project"** generation.

## **The Core Philosophy: "Flattened Paths"**

LLMs struggle with deep directory structures in conversation. It is better to keep the chat context "flat" while embedding the *intent* of structure in the filenames.

ParseAI's **Clean Reconstruction** feature (`--clean-project`) exploits this. It looks for "Type Prefixes" and "Snake Case" to explode flat filenames into a deep project tree.

**The Formula:**
`{TYPE_PREFIX}_{PATH_TO_FILE}_{FILENAME}.{EXT}`

**Examples:**
*   **Intent**: `src/backend/server.py`
*   **LLM Output**: `py_src_backend_server.py`
*   **ParseAI Result**: `src/backend/server.py` (Prefix stripped, underscores split)

---

## **The "God Mode" System Prompt**

Copy and paste this into your Custom Instructions or System Prompt. It forces the LLM to adhere to the ParseAI protocol strictly.

```markdown
### SYSTEM INSTRUCTIONS: CODE & FILE GENERATION PROTOCOL

**1. STRICT FILE NAMING (The Flattened Path Rule)**
You are generating files for the ParseAI reconstruction engine. You MUST flatten your directory structure into snake_case filenames using specific prefixes.

*   **Format**: `{PREFIX}_{PATH_SEGMENTS}_{FILENAME}.{EXT}`
*   **Prefixes (Mandatory)**:
    *   `py_`   : Python Code
    *   `sh_`   : Shell/Bash Scripts
    *   `js_`   : JavaScript/TypeScript
    *   `json_` : Configs/Data
    *   `md_`   : Documentation
    *   `txt_`  : Notes/Scratchpad

*   **Examples**:
    *   WANT: `src/utils/logger.py`  -> GENERATE: `py_src_utils_logger.py`
    *   WANT: `tests/test_main.py`   -> GENERATE: `py_tests_test_main.py`
    *   WANT: `config/app/settings.json` -> GENERATE: `json_config_app_settings.json`
    *   WANT: `deploy.sh`            -> GENERATE: `sh_deploy.sh`

**2. CODE BLOCK FORMATTING**
You MUST use strict code fences with the filename appended to the language tag.

*   **Syntax**:
    \`\`\`language:filename
    [Code Content]
    \`\`\`

*   **Example**:
    \`\`\`python:py_core_server.py
    print("Server Starting...")
    \`\`\`

**3. VERSIONING STRATEGY**
*   **Code Files**: Keep filenames STATIC. Do not append `_v1`, `_v2` to the filename. 
    *   *Correct*: `py_core_server.py` (The tool handles overwrites/versioning).
    *   *Incorrect*: `py_core_server_v2.py` (Breaks imports).
*   **Versioning**: Put the version number in the **FILE HEADER** (comment), not the filename.

**4. HANDLING UPDATES**
When updating a file, output the **ENTIRE** file content again with the SAME filename. Do not output partial diffs unless explicitly asked.
```

---

## **How It Works (The Pipeline)**

1.  **You Prompt**: "Create a basic flask app with a routes file."
2.  **LLM Generates**:
    *   `py_app.py` (Main entry point)
    *   `py_routes_main.py` (Routes controller)
3.  **You Run**: 
    ```bash
    ./parser_ai/run_parser.sh --clean-project
    ```
4.  **ParseAI Delivers**:
    *   `merged_project/app.py`
    *   `merged_project/routes/main.py`

## **Manual Overrides**

If you simply want to name a file without the structural logic, just avoid the prefixes or the underscores.

*   `script.py` -> Extracts as `script.py` (No reconstruction).
*   `my_script.py` -> Extracts as `my/script.py` (If suffix reconstruction hits), OR just use `python:script.py`.

*Tip: Trust the prefix system. It avoids collisions and keeps your chat file list sorted alphabetically by type!*
