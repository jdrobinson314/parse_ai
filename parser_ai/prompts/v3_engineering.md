Project Structure and File Management
1. File Creation: Only create a file when asked. When creating files, create files according to their prescribed format. Artifacts, code blocks, command references need to be properly formatted ( reference formats 1, 2, 3 ). Path files logically.
2. Project Directory Structure
   * Enforce separation of concerns via a rigid tree structure:
      * Initialization (Root): .gitignore, README, dependencies.
      * Distribution: 
         * build/: Core application distribution folder.
      * Logic:
         * src/: Core application source code.
         * src/scripts/: Utility and automation scripts.
         * src/qlib/: Shared internal modules.
      * Resources:
         * config/: Static settings.
         * assets/: Application specific media and visuals.
         * data/: Raw and processed operational datasets.
      * Quality Assurance & Docs:
         * tests/: Automated testing suites.
         * manuals/: User manuals and user facing project documentation.
         * src/docs/: Project source manuals and source code documentation.
      * Input:
         * input/: Input source folder ( for supported batch operations )
      * Output:
         * output/: Application generated logs, runtime outputs, and temp files.
3. File Naming and Metadata Protocols
   * Source Code (Static):
      * Rule: No version numbers in filenames (ensure import and source reference stability).
      * Format: project_descriptor.ext
      * Versioning: Internal file headers only.
   * Logs (And dynamic inquiries about the project):
      * Rule: Header must include timestamp or version ID (ensures historical tracking). File name must include version number. 
         * Format: log_descriptor_vXX.ext
   * Artifacts:
      * Rule: Header must include timestamp or version ID (ensures historical tracking). File name must include version number.
         * Format: artifact_descriptor_vXX.ext
   * Metadata Headers:
      * All primary source files must begin with a standardized block containing: File Path/Name, Version Identifier, and Context/Compatibility Notes, as well as thorough project level description.
         * Reference example format 2.
4. Artifact Generation and Presentation
   * When using backticks to present code, commands, or file content in documentation, present the following information: type of data, path within the project, and file name with extension.
      * Reference example Format 1.
Example Format 1 ( file naming and pathing ):
```bash:/src/scripts/launch.sh
# This signifies a bash script residing at the specified path.
```
Example Format 3 ( code block ):
```bash
# This signifies a bash command set code block
```
Example Format 2 ( file header ):
```meta:[path]/[filename].[ext]
# Filename: [path]/[filename].[ext]
# Version: [Time Stamp], [File Version Number]
# Context: [ File relevant context, compatibility information ]
# Description: [ A thorough explanation of the file’s purpose within the project. ]
# --------------------------------------------------
```