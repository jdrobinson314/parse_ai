# **How To: Rebuilding Project Structures**

ParseAI isn't just a log viewer; it's a **Filesystem Compiler**. It allows you to build complex, nested software projects entirely within a chat interface and export them to a working folder on your computer.

## **1. The Core Concept**

When you code with an AI, you usually get snippets scattered across a long conversation. Copy-pasting them into folders is tedious and error-prone.

ParseAI automates this by reading the **Output Path** directly from the chat code block (if you prompt the AI correctly).

*   **Chat Input**:
    ```text
    > Create the database config.
    > ```json:config/db.json
    > { "host": "localhost" }
    > ```
    ```

*   **ParseAI Action**:
    Detects `config/db.json` -> Creates `config/` folder -> Writes `db.json`.

## **2. The Workflow: "Chat-Extract-Merge"**

### **Step A: The Prompt**
Ensure your AI knows to output paths. (See `parser_ai/prompts/v1_standard.md`).

### **Step B: The Chat**
Iterate on your code.
*   "Write `src/main.py`."
*   "Wait, update `src/main.py` to fix that bug."
*   "Now create `tests/test_main.py`."

### **Step C: The Parse**
Run ParseAI with the **Clean Project** flag.

```bash
# Windows
.\parser_ai\run_parser.ps1 --clean-project

# Linux/Mac
./parser_ai/run_parser.sh --clean-project
```

### **Step D: The Result**
Look in `output/<SessionName>_files/merged_project/`.
You will see:
```text
merged_project/
├── src/
│   └── main.py  (The LATEST version from the chat)
├── config/
│   └── db.json
└── tests/
    └── test_main.py
```

## **3. Understanding "Merge" Logic**

What happens if the AI rewrites a file 5 times?

*   **`files/` folder (The Archive)**: You get `001_main.py`, `002_main.py`... `005_main.py`. Nothing is lost.
*   **`merged_project/` folder (The Build)**: You get **ONLY** the contents of `005_main.py` inside `src/main.py`.

ParseAI applies a **"Last-Write-Wins"** strategy. It sequentially processes the chat from start to finish. If a file is defined again, it overwrites the previous version in the `merged_project` output. This ensures your project represents the *final state* of the conversation.

## **4. Best Practices**

1.  **Use `--clean-project` (`-cp`)**: This is the "Magic Button". It combines Reconstruction (`-r`) and Merging (`-m`) into a standard folder.
2.  **Versioning in Headers**: Ask the AI to include a standard header (as shown in `parser_ai/prompts/v2_advanced.md`). This helps you verify which "version" of the file ended up in the project.
3.  **One Session per Feature**: Start a new chat session for major features to keep the log file size manageable and the `merged_project` context clean.
