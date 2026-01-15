Project Structure and File Management

1. File Creation: Only create a file when asked. When creating files, create files according to their prescribed format. Artifacts, code blocks, command references need to be properly formatted. Path files logically.

2. Project Directory Structure
   * Enforce separation of concerns via a rigid tree structure:
      * Initialization (Root): .gitignore, README, dependencies.
      * Logic:
         * src/: Core application source code.
         * src/scripts/: Utility and automation scripts.
         * src/modules/: Shared internal modules.
      * Resources:
         * config/: Static settings.
         * assets/: Application specific media and visuals.
      * Quality Assurance & Docs:
         * tests/: Automated testing suites.
         * docs/: Project documentation.
      * Output:
         * output/: Runtime logs and generated files.

3. File Naming and Metadata Protocols
   * Source Code (Static):
      * Rule: No version numbers in filenames.
      * Format: project_descriptor.ext
      * Versioning: Internal file headers only.
   * Artifacts:
      * Rule: Historical artifacts can have versions in filenames.
      * Format: artifact_descriptor_vXX.ext

4. Artifact Generation and Presentation
   * **Crucial**: Code blocks must indicate the **full relative path** in the fence label.
   
   **Format 1 (File Generation)**:
   ```language:path/to/filename.ext
   # Code content...
   ```
   
   **Format 2 (File Header Standard)**:
   All primary source files must begin with this block:
   ```text
   # Filename: [path]/[filename].[ext]
   # Version: [Time Stamp], [File Version Number]
   # Context: [ File relevant context, compatibility information ]
   # Description: [ A thorough explanation of the file’s purpose within the project. ]
   # --------------------------------------------------
   ```
