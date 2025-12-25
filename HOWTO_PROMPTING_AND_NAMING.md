# **How To: System Prompts & Automatic Naming**

This guide details the relationship between strict System Prompts (used to control the LLM's output) and ParseAI's extraction capabilities.

## **The Concept**

ParseAI is built to recognize specific patterns in the LLM's output. By enforcing a strict "Protocol" in your System Prompt, you guarantee 100% extraction accuracy and enable powerful post-processing workflows.

## **1. The Recommended System Prompt**

Copy and paste the following into your LLM's system instructions. This protocol enforces **Static Filenames** inside **Named Code Blocks**, which ParseAI detects automatically.

```markdown
### SYSTEM PROTOCOL: FILE GENERATION & FORMATTING

**1. NAMING CONVENTION (Split Logic)**

* **A. BASE CODE & CONFIGS (.py, .sh, .json, .yaml, .md)**
    * *Rule:* Filenames MUST remain static to allow programmatic linking/importing. **NO** version numbers in the filename.
    * *Format:* `{PREFIX}_{PROJECT}_{DESCRIPTOR}.{EXT}`
    * *Example:* `py_core_tensor_loader.py` (NOT `_v01.py`)

* **B. TEXT & LOGS (.txt)**
    * *Rule:* These are snapshots/artifacts. **INCLUDE** version numbers or timestamps in the filename.
    * *Format:* `{PREFIX}_{PROJECT}_{DESCRIPTOR}_v{VERSION}.txt`
    * *Example:* `log_core_debug_dump_v04.txt`

* **PREFIXES:**
    * `py_` : Python scripts
    * `sh_` : Bash/Shell scripts
    * `cfg_` : Configuration data
    * `txt_` / `doc_` : Text/Notes

**2. CODE BLOCK FORMATTING (Strict)**
Do not use generic language tags. You must append the specific filename to the language identifier.

* *Format:* ` ```language:filename `
* *Example:* ` ```python:py_core_main.py `
* *Example:* ` ```text:txt_project_notes_v02.txt `

**3. SHEBANG & INTERPRETER RULES (Linux Context)**
* **Python:** MUST start with: `#!/usr/bin/env python3`
* **Bash:** MUST start with: `#!/bin/bash`
* **Environment:** Assume `python3` binary usage.

**4. MANDATORY HEADER METADATA**
Since filenames no longer carry version info for code, the Header is the **Source of Truth** for versioning.

* **For Python/Shell/Configs:**
    ```python
    #!/usr/bin/env python3
    # ------------------------------------------------------------------
    # FILENAME: {Exact Filename}
    # VERSION:  v{XX} (Increment this manually here)
    # CONTEXT:  {Linux/Windows/Dual}
    # ------------------------------------------------------------------
    ```
```

---

## **2. How ParseAI Reacts**

When the model follows the prompt above, it outputs blocks like:

> \`\`\`python:py_core_main.py
> print("Hello")
> \`\`\`

ParseAI's "Golden Standard" heuristic sees the `python:py_core_main.py` tag.
1.  **Detection**: It instantly identifies this as a file to be saved.
2.  **Extraction**: It extracts `py_core_main.py`.
3.  **Saving**: It saves the content to `output/<RunName>_files/py_core_main.py`.

## **3. Post-Processing & Renaming**

The System Prompt above enforces *prefixes* (e.g., `py_`) to help the LLM organize its context. However, you might not want these prefixes in your actual project folder.

ParseAI provides flags to handle this **automatically** during the extraction phase:

### **A. Stripping Prefixes (`--strip`)**
You can remove the "LLM-helper" prefixes while keeping the filenames clean on disk.

```bash
# Removes "py_" and "sh_" from the start of filenames
./parser_ai/run_parser.sh --strip "^py_" --strip "^sh_"
```
* **Input (from LLM)**: `py_core_main.py`
* **Output (on Disk)**: `core_main.py`

### **B. Handling Static Names (`--add-numbering`)**
The System Prompt enforces **static filenames** (no `_v02.py` in the filename) to allow imports to work.
If you want to keep *history* of how the file changed over a long conversation, use the numbering flag:

```bash
./parser_ai/run_parser.sh -n
```
* **Output 1**: `001_py_core_main.py`
* **Output 2** (later in chat): `005_py_core_main.py`

This gives you the best of both worlds:
1.  **AI Consistency**: The AI sees stable filenames (`import core_main`), so it doesn't get confused.
2.  **User Control**: You get clean filenames or chronological version strings on your hard drive.
### **C. Clean Project Reconstruction (`--clean-project`)**

The most powerful way to use ParseAI is to allow it to build your folder structure for you. The parser now has intelligent logic to **strip type prefixes** when rebuilding the project tree.

**The Strategy:**
Prompt the AI to use "snake_case" filenames that represent the path, starting with a type prefix (`py_`, `sh_`, `json_`).

**How to Prompt:**
> "Name your files with a type prefix and snake_case path. For example, `py_core_utils.py` will become `core/utils.py`."

**The Result:**
When you run:
```bash
./parser_ai/run_parser.sh --clean-project
```

ParseAI performs **"Clean Reconstruction"**:
1.  **Detects Prefix**: Sees `py_core_utils.py`. Recognizes `py_` is a helper prefix.
2.  **Strips Prefix**: Removes `py_`. Remaining: `core_utils.py`.
3.  **Reconstructs Path**: Splits by underscores. `core_utils.py` -> `core/utils.py`.

| AI Output Name | Final Clean Path |
| :--- | :--- |
| `py_main.py` | `main.py` |
| `py_core_server.py` | `core/server.py` |
| `sh_scripts_deploy.sh` | `scripts/deploy.sh` |
| `json_config_app_settings.json` | `config/app/settings.json` |

This allows you to keep a flat, easily referencable list of files in the chat ("Check `py_core_server.py`"), while generating a perfectly deep-nested project structure on disk.
