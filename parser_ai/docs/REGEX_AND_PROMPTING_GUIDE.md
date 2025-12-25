# Advanced Parsing & Prompting Guide

This guide details how to leverage the advanced custom parsing features of ParseAI and how to prompt your AI models (Google AI Studio, Gemini, ChatGPT, Claude) to produce output that is perfectly formatted for extraction.

## 1. The One-Liner Regex System (`--parse`)

ParseAI allows you to inject custom parsing logic directly from the command line using the `--parse` argument. This is powerful when you are dealing with log files or chat exports that use different conventions for naming files.

### How it Works
The parser accepts a Python Regular Expression. **Crucially, you must use a capture group `(...)` to indicate which part of the pattern is the filename.**

### Examples

#### Scenario A: The "Save As" Pattern
Your model outputs: `Save this code as: server.js`
*   **Regex**: `Save this code as:\s*(.+)`
*   **Command**:
    ```bash
    ./parser_ai/run_parser.sh --parse "Save this code as:\s*(.+)"
    ```

#### Scenario B: The Bracket Style
Your model outputs: `[FILE] /src/components/Button.tsx`
*   **Regex**: `\[FILE\]\s+(.+)`
*   **Command**:
    ```bash
    ./parser_ai/run_parser.sh --parse "\[FILE\]\s+(.+)"
    ```

#### Scenario C: Complex Arrows
Your model outputs: `>>> writing to: config.yaml`
*   **Regex**: `>>> writing to:\s+([a-zA-Z0-9_.]+)`
*   **Command**:
    ```bash
    ./parser_ai/run_parser.sh --parse ">>> writing to:\s+([a-zA-Z0-9_.]+)"
    ```

---

## 2. System Prompts for AI Models

To get the best results, you should instruct your AI model on how to format code blocks. Copy and paste the following into your **System Instructions** or the beginning of your chat.

### The "ParseAI Standard" Prompt
Use this prompt to ensure maximum compatibility with the default extraction logic.

> **System Instruction:**
> When you write code that should be saved to a file, you must follow this format:
>
> 1.  **Strict Header**: Precede the code block with a header in the format `### File: path/to/filename.ext`.
> 2.  **Inline Convention** (Preferred): Alternatively, specify the filename directly in the code fence language tag, like so: 
>     \`\`\`python: backend/server.py
>     ... code ...
>     \`\`\`
> 3.  **No Ambiguity**: Do not provide code without a filename if it is meant to be saved. Anonymous blocks will be ignored or saved as generic snippets.

### The "Inline-Only" Prompt (Compact)
If you want cleaner chat logs, force the model to use the inline syntax.

> **System Instruction:**
> ALWAYS specify the target filename in the code block language tag. 
> Example: 
> \`\`\`javascript: src/utils.js
> console.log("files");
> \`\`\`
> Never use generic tags like \`\`\`javascript\`\`\` for project files.

---

## 3. Understanding Code Block Types

It is important to understand how ParseAI distinguishes between different types of code blocks found in a conversation.

### Type A: Named Files (Extracted)
These are blocks that the parser can confidently associate with a specific filename.
*   **Source**: A `### File:` header or an inline `lang: filename` tag.
*   **Result**: Created as `files/actual_name.py`.

### Type B: Anonymous Blocks (Archived)
These are code blocks that look like code but have no filename associated with them.
*   **Source**: A plain ` ```python ` block with no preceding header.
*   **Result**: Saved to `code_blocks/block_00X.py`.
*   **Use Case**: One-off commands, explanations, or snippets that don't belong in the codebase.

### Type C: Misfires & Ghosts (Suppressed)
Sometimes a model might hallucinate a header but fail to provide code, or provide a filename in a tiny block.
*   **Result**: The parser has logic to ignore headers that aren't followed by code, preventing 0-byte "Ghost Files" from cluttering your output.

---

## 4. Tips for Success
*   **Use Extensions**: Always ask the model to include file extensions (.py, .js, .md).
*   **Avoid Spaces**: Filenames with spaces usually break standard regexes. Use underscores or camelCase.
*   **Relative Paths**: Encouraging the model to output `apps/main.py` instead of just `main.py` helps keep your extracted files organized in the output directory.
