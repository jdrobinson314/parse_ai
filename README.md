# **ParseAI: Google AI Studio Log Parser**

The Missing Link for AI Studio Workflows  
ParseAI bridges the gap between Google AI Studio's raw JSON exports and a usable local development environment. It turns conversation logs into readable documentation and automatically refactors code blocks into actual files.

## **🚀 Why ParseAI?**

Google AI Studio is powerful, but extracting your work can be tedious. When you export a conversation, you get a complex JSON file containing metadata, "thought" chains, and mixed formatting.

**ParseAI solves this by:**

1. **Decoding the Context**: It strips away the JSON noise, presenting the conversation (including hidden "thoughts") in a clean, human-readable format.  
2. **Liberating the Code**: It acts as a virtual file system parser. If the AI writes code in the chat, ParseAI detects it, names it, and saves it to your disk automatically.

## **⚙️ Core Workflow**

The tool operates on a simple "Ingest → Process → Extract" pipeline:

1. **Export**: Download your session as JSON from Google AI Studio.  
2. **Ingest**: Drop the JSON file into the `ingest/` folder.  
3. **Run**: Execute the parser script.  
4. **Result**:  
   * **Readable Logs**: A formatted markdown file appears in `output/` (e.g., `MySession_parsed.md`).  
   * **Source Code**: A folder appears (e.g., `output/MySession_files/`) containing every script, config, or snippet the AI generated.

## **🛠️ Installation & Setup**

### **Prerequisites**

* **Python 3.6+** (Standard on most Linux distributions)  
* No complex virtual environment required for standard use.

### **Quick Setup**

```bash
# 1. Clone the repository
git clone https://github.com/jdrobinson314/parse_ai.git
cd parse_ai

# 2. Ensure execution permissions (Linux/Mac)
chmod +x parser_ai/run_parser.sh
```

## **💻 Usage**

### **Basic Execution**

The included launcher script handles path discovery and execution.

```bash
./parser_ai/run_parser.sh
```

*This processes every JSON file found in `ingest/` and saves results to `output/`.*

### **Command Line Arguments**

You can customize how files are named and organized using flags.

| Flag | Short | Description | Example |
| :---- | :---- | :---- | :---- |
| `--add-numbering` | `-n` | **Chronological Sorting**. Prepends `001_`, `002_` to files. Useful for tracking code evolution. | `001_script.py`, `002_updated_script.py` |
| `--strip` | `-s` | **Prefix Removal**. Strips specific regex patterns from filenames. Can be used multiple times. | `--strip "^py_" --strip "^sh_"` |
| `--reconstruct` | `-r` | **Structure Recovery**. Project flat filenames into directories using underscores. | `src_main.py` -> `src/main.py` |
| `--help` | `-h` | Show full help message. |  |

**Example Command:**

```bash
# Run with numbering enabled and strip "temp_" from filenames
./parser_ai/run_parser.sh -n --strip "^temp_"

# Reconstruct directory structure from underscores
./parser_ai/run_parser.sh --reconstruct
```

## **🧠 Intelligent Code Extraction**

ParseAI uses a multi-layered heuristic engine to determine where code should go. It scans your AI conversation for specific cues.

### **1. The "Golden Standard" (Code Fence)**

The most robust method. If the language tag in the markdown code block includes a colon and a path, ParseAI uses it immediately.

**Input in AI Studio:**

> Here is the updated server code:
> ```python:src/backend/server.py
> print("Starting server...")
> ```

**Output on Disk:**

`output/SessionName_files/src/backend/server.py`

### **2. Header Association**

If no filename is in the fence, the parser looks at the line immediately preceding the block.

* `### File: script.js`
* `**Filename: config.json**`
* `Save this as: main.py`

### **3. The "Tiny Block" Heuristic**

Sometimes the AI puts the filename in its own tiny code block before the actual code.

* If a block is <100 chars, has no spaces, and looks like a path, it becomes the name for the *next* block.

### **4. Duplicate Handling**

* **Version Control**: If `main.py` is generated three times in one conversation, ParseAI will overwrite it sequentially by default, ensuring you have the *final* version.  
* **Numbering**: Use `-n` if you want to keep all versions (`001_main.py`, `005_main.py`).

## **📂 Directory Structure**

```text
.
├── ingest/                  # DROP ZONE: Place Google AI Studio JSON exports here
├── parser_ai/               # Core Application Code
│   ├── apps/
│   │   ├── json_parser.py   # Log processing logic
│   │   └── extractor.py     # Regex & file saving logic
│   ├── docs/                # Extended Documentation
│   └── run_parser.sh        # Entry point script
├── output/                  # ARTIFACTS: Generated logs and extracted code
└── README.md
```

## **📚 Documentation & Resources**

* [**Plugin Roadmap**](parser_ai/docs/PLUGIN_ROADMAP.md): Plans for supporting other LLM export formats.  
* [**Prompting Guide**](parser_ai/docs/REGEX_AND_PROMPTING_GUIDE.md): **Crucial Reading.** Learn how to prompt Google AI Studio to output code in the format ParseAI likes best (System Prompts included).
* [**System Prompts & Naming**](HOWTO_PROMPTING_AND_NAMING.md): Detailed guide on how strict system prompts work with ParseAI's automatic renaming and versioning features.
* [**User Guide**](parser_ai/docs/USER_GUIDE.md): Complete instructions on installation, usage, and command-line arguments.
* [**Source Code Reference**](parser_ai/docs/SOURCE_CODE_REFERENCE.md): A technical look at the internal logic of ParseAI's modules.

## **License**

© 2025 James D. Robinson, and Gemini. Licensed under MIT.