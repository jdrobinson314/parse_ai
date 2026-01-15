# Features Preview

This document outlines planned and potential features for the Parser AI.

## Parsing Logic Enhancements

### 1. Metadata Extraction
**Goal:** Extract rich metadata from the input JSON and prepend it to the output text.
**Data Points:**
- `runSettings.model` (e.g., `models/gemini-3-pro-preview`)
- `runSettings.temperature`
- Timestamp (if available in filename or content)
- Token counts

### 2. Thought/Reasoning Support
**Goal:** Handle `isThought: true` blocks intelligently.
**Options:**
- **Separate Section:** Group "thoughts" separately from the final response.
- **Collapsible:** Use HTML `<details>` tags to make thoughts collapsible in Markdown viewers.
- **Toggle:** Command-line flag to include/exclude thoughts.

### 3. Role Mapping & Formatting
**Goal:** Clean up role names and formatting.
- Map `model` -> `🤖 AI`
- Map `user` -> `👤 User`
- Ensure visual separation between turns (e.g., horizontal rules `---`).

### 4. Code Block Normalization
**Goal:** Ensure code blocks in the output are properly fenced and language-tagged, even if the raw text is slightly malformed.

### 5. Multi-Output Formats
**Goal:** Support outputting to:
- `text` (Raw textual representation, current default)
- `markdown` (Enhanced formatting)
- `html` (For browser viewing)
