# ParseAI Plugin Roadmap

## Overview
ParseAI aims to evolve into a highly extensible framework where users can define custom parsing logic, file detection strategies, and post-processing steps through a plugin interface.

## 1. Custom Parsing Patterns (Phase 1 - Completed)
- **Feature**: CLI support for custom regex patterns.
- **Usage**: `--parse "REGEX_PATTERN"`
- **Status**: Implemented. Users can now inject one-liner regexes to capture filenames from arbitrary text headers.

## 2. Python Plugin API (Phase 2 - Planned)
- **Goal**: Allow users to write Python classes that hook into the extraction lifecycle.
- **Interface**:
  ```python
  class ParserPlugin:
      def on_text_scan(self, text):
          """Return list of detected file candidates."""
          pass
      
      def on_block_extracted(self, content, lang):
          """Modify block content or determine filename."""
          pass
  ```
- **Loading**: Plugin files placed in `plugins/` directory automatically loaded.

## 3. Post-Processing Hooks (Phase 3 - Planned)
- **Goal**: Auto-formatting, linting, or testing extracted code.
- **Examples**:
  - Auto-run `black` on extracted Python files.
  - Auto-run `npm install` for `package.json`.

## 4. Metadata Extraction (Phase 4 - Planned)
- **Goal**: defining rich metadata extraction rules (e.g. author, version, dependencies) alongside file content.

## 5. Advanced Naming & Ordering (Phase 5 - Completed)
- **Goal**: Manage large-scale outputs (1000+ files) with precise ordering and namespace control.
- **Chronological Tracking**:
  - **Implemented**: CLI flag `--add-numbering` / `-n` adds `001_` prefixes.
- **Prefix Argument System**:
  - **Implemented**: CLI flag `--strip` / `-s` accepts regex patterns to clean filenames (e.g. `-s "^py_"`).

## Contribution
We welcome community contributions to define standard patterns for common LLM outputs (e.g. ChatGPT, Claude, standard markdown blocks).
