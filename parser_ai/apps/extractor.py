import re
import os

class CodeExtractor:


    def __init__(self, output_base_dir):
        self.output_base_dir = output_base_dir

    def extract_from_text(self, text, source_filename):
        """
        Parses text for file definitions and writes them to disk.
        
        Expected format:
        ### File <N>: <filename>
        **Description:** <description>
        ```<lang>
        <code>
        ```
        """
        # Create a directory for this source file's extractions
        source_name = os.path.splitext(os.path.basename(source_filename))[0]
        extraction_dir = os.path.join(self.output_base_dir, f"{source_name}_files")
        
        # Regex to find file blocks
        # 1. Header: ### File \d+: (filename)
        # 2. Description (Optional): **Description:** (text)
        # 3. Code Block: ```(lang)?\n(content)\n```
        
        # We'll iterate through the text since the blocks might be separated by conversational text
        
        file_pattern = re.compile(
            r'### File \d+: `?([^\n`]+)`?'  # Capture filename, handle optional backticks
            r'(?:\s*\*\*Description:\*\*\s*([^\n]+))?' # Capture description (greedy to EOL)
            r'.*?' # Non-greedy match for intervening text
            r'```(\w+)?\n([\s\S]+?)\n```', # Capture language (optional) and content
            re.DOTALL | re.MULTILINE
        )

    def extract_from_text(self, text, source_filename, custom_patterns=None, add_numbering=False, strip_patterns=None, reconstruct=False):
        """
        Parses text for ALL code blocks and writes them to disk sequentially.
        Ignores headers or filenames in the text.
        """
        # Create a directory for this source file's extractions
        source_name = os.path.splitext(os.path.basename(source_filename))[0]
        base_extraction_dir = os.path.join(self.output_base_dir, f"{source_name}_files")
        
        dir_blocks = os.path.join(base_extraction_dir, "code_blocks")
        dir_files = os.path.join(base_extraction_dir, "files")
        # New: Reconstructed directory
        dir_reconstructed = os.path.join(base_extraction_dir, "reconstructed")

        manifest = []
        count = 0

        # --- TOKEN TYPES ---
        # 1. FILENAME_HEADER (Explicit headers)
        filename_patterns = [
            # Standard "Header: Value"
            re.compile(r'### File \d+: `?([^\n`]+)`?', re.IGNORECASE),
            # "Save as: main.py" - Standard loose name
            re.compile(r'(?:save this as|(?:\bfile|\bfilename)\s*:)\s*`?([a-zA-Z0-9_./-]+)`?', re.IGNORECASE),
            # "Create main.py" - STRICT: Must have extension to avoid "Create a directory"
            re.compile(r'(?:create)\s+`?([a-zA-Z0-9_./-]+\.[a-zA-Z0-9]+)`?', re.IGNORECASE)
        ]

        # 1b. CUSTOM PATTERNS (User provided)
        if custom_patterns:
            for pattern_str in custom_patterns:
                try:
                    # simple validation/compilation
                    # We assume the user provides a regex where group 1 is the filename
                    cp = re.compile(pattern_str, re.IGNORECASE | re.MULTILINE)
                    filename_patterns.append(cp)
                    print(f"Added custom pattern: {pattern_str}")
                except Exception as e:
                    print(f"Failed to compile custom pattern '{pattern_str}': {e}")

        # 2. CODE_BLOCK (Fenced content)
        # Modified to capture the entire line after ``` as the 'lang' group for later parsing
        block_pattern = re.compile(r'```([^\n]*)\n([\s\S]+?)```', re.DOTALL)

        # Collect all "Events" with their positions
        events = []

        # Find Headers
        for p in filename_patterns:
            for m in p.finditer(text):
                fname = m.group(1).strip()
                if fname:
                    events.append({
                        'type': 'filename',
                        'start': m.start(),
                        'name': fname,
                        'source': 'header'
                    })

        # Find Blocks
        for m in block_pattern.finditer(text):
            events.append({
                'type': 'block',
                'start': m.start(),
                'lang': m.group(1).strip() if m.group(1) else "text",
                'content': m.group(2)
            })

        # Sort events by position in text
        events.sort(key=lambda x: x['start'])

        if events:
            # Create subdirectories
            # Always create blocks and files
            dirs_to_create = [dir_blocks, dir_files]
            if reconstruct:
                dirs_to_create.append(dir_reconstructed)

            for d in dirs_to_create:
                if not os.path.exists(d):
                    os.makedirs(d)

            print(f"Created extraction directories in: {base_extraction_dir}")

            # Calculate padding width
            total_blocks = sum(1 for e in events if e['type'] == 'block')
            width = len(str(total_blocks))
            pad_width = max(4, width)
            
            current_filename = None
            processed_filenames = set()
            file_versions = {} # Track version count for each file
            reconstructed_versions = {} # Track version count for reconstructed files
            
            # File creation counter for numbering feature
            file_creation_count = 0 

            for event in events:
                if event['type'] == 'filename':
                    # Validate Detected Name
                    if self.is_valid_filename(event['name']):
                        current_filename = event['name']
                        # Defer creation until we have content
                        # Just log that we found a header
                        print(f"Detected header references file: {current_filename}")
                    else:
                        current_filename = None # Reset if invalid header found

                elif event['type'] == 'block':
                    content = event['content'].strip()
                    raw_lang = event['lang'] or ""
                    
                    lang = raw_lang.strip()
                    inline_filename = None

                    # Parse "lang: filename" from code fence
                    # Pattern: "python: my_script.py"
                    meta_match = re.match(r'^([a-zA-Z0-9_\-+#.]+):\s*(.+)$', lang)
                    if meta_match:
                        lang = meta_match.group(1).strip()
                        candidate = meta_match.group(2).strip()
                        if self.is_valid_filename(candidate):
                            inline_filename = candidate

                    # LOGIC: Check for "Tiny Block" -> Treat as Filename
                    # Only done if no inline filename was found in the fence
                    if not inline_filename and '\n' not in content and ' ' not in content and len(content) < 100 and '.' in content:
                        candidate_name = content.strip()
                        if self.is_valid_filename(candidate_name):
                            current_filename = candidate_name 
                            print(f"Detected inline block references file: {current_filename}")
                            continue # Skip extraction for this block - it is just a name

                    # Regular Content Block
                    count += 1
                    filename = f"block_{count:0{pad_width}d}.{lang}"
                    
                    # 1. Write to Code Blocks folder
                    saved_path = self._write_file(dir_blocks, filename, event['content'], lang)
                    
                    entry = {
                        "file": os.path.basename(saved_path),
                        "description": "Isolated code block",
                        "language": lang
                    }

                    # Determine target filename (Inline takes precedence over Header)
                    target_filename = inline_filename if inline_filename else current_filename

                    # 2. If Associated: Write to Files folder (and optionally Reconstructed)
                    if target_filename:
                        entry["associated_filename"] = target_filename
                        
                        # --- COMMON PRE-PROCESSING ---
                        # Base sanitization
                        base_sanitized = self.sanitize_filename(os.path.basename(target_filename))
                        
                        # A. Strip Prefixes (String/Regex) - Applies to ALL potential outputs
                        if strip_patterns:
                            for pattern in strip_patterns:
                                if pattern:
                                    base_sanitized = re.sub(pattern, '', base_sanitized)
                        
                        file_creation_count += 1
                        
                        # Define Numbering Prefix
                        num_prefix = ""
                        if add_numbering:
                             num_prefix = f"{file_creation_count:03d}_"


                        # --- PATH 1: FLAT FILES (Default) ---
                        # Logic: Numbering + Stripped Name
                        flat_name = f"{num_prefix}{base_sanitized}"
                        dest_path_flat = os.path.join(dir_files, flat_name)
                        
                        self._save_content_safely(dest_path_flat, content, file_versions)
                        entry["saved_as"] = flat_name

                        # --- PATH 2: RECONSTRUCTED (Optional) ---
                        if reconstruct:
                            # 1. Identify and Strip Type Prefix for CLEAN Reconstruction
                            clean_base = base_sanitized
                            type_prefix = None
                            
                            # Common prefixes to strip for "Project Structure", but keep for "Sorted Merge"
                            # e.g. py, sh, txt, json, cfg, js, html, css, md
                            known_prefixes = ['py', 'sh', 'txt', 'json', 'cfg', 'js', 'html', 'css', 'md', 'src', 'test', 'config']
                            
                            for p in known_prefixes:
                                if clean_base.lower().startswith(f"{p}_"):
                                    type_prefix = p
                                    # Strip it for reconstruction
                                    clean_base = clean_base[len(p)+1:] 
                                    break
                            
                            # 2. Logic: Reconstruct directory structure from underscores (using CLEAN base)
                            base, ext = os.path.splitext(clean_base)
                            
                            reconstructed_rel_path = clean_base # Default fallback
                            
                            if '_' in base:
                                parts = base.split('_')
                                # Conservative Reconstruction:
                                # "core_span_classifier" -> "core/span_classifier.py"
                                
                                if len(parts) > 1:
                                    last = parts.pop()
                                    second_last = parts.pop()
                                    leaf_name = f"{second_last}_{last}"
                                    leaf_filename = leaf_name + ext
                                    
                                    if parts:
                                        reconstructed_rel_path = os.path.join(*parts, leaf_filename)
                                    else:
                                        reconstructed_rel_path = leaf_filename
                                else:
                                    reconstructed_rel_path = clean_base
                            
                            # Apply Numbering to the ROOT of reconstructed path
                            final_reconstructed_name = f"{num_prefix}{reconstructed_rel_path}"
                            dest_path_reconstructed = os.path.join(dir_reconstructed, final_reconstructed_name)
                            
                            self._save_content_safely(dest_path_reconstructed, content, reconstructed_versions)
                            
                            entry["reconstructed_path"] = final_reconstructed_name
                            
                            # 3. Calculate Sorted Path for Merge (Prefix/CleanPath)
                            if type_prefix:
                                # If we stripped a prefix, use it as the sorting folder
                                entry["sorted_path"] = os.path.join(type_prefix, reconstructed_rel_path)
                            else:
                                # If no prefix, maybe sort by extension? OR just use root.
                                # User said "sorted-by-type".
                                # If file is "main.py", explicit type is better?
                                # Let's try to infer from extension if no prefix found?
                                inferred_type = lang if lang else "misc"
                                # Check extension if lang is generic
                                if not lang and ext:
                                    inferred_type = ext.lstrip('.')
                                
                                entry["sorted_path"] = os.path.join(inferred_type, reconstructed_rel_path)

                        # Consume the header context since we've processed a block
                        current_filename = None 
                        
                    manifest.append(entry)

        # Write Manifest
        if manifest:
            import json
            manifest_path = os.path.join(base_extraction_dir, "manifest.json")
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
            print(f"Created manifest: {manifest_path}")
            
        return count


    def rotate_file(self, filepath, version):
        """
        Renames an existing file to filepath_v{version}.ext
        """
        if not os.path.exists(filepath):
            return

        dirname = os.path.dirname(filepath)
        basename = os.path.basename(filepath)
        name, ext = os.path.splitext(basename)
        
        new_name = f"{name}_v{version}{ext}"
        new_path = os.path.join(dirname, new_name)
        
        try:
            os.rename(filepath, new_path)
            print(f"Rotated previous version to: {new_path}")
        except Exception as e:
            print(f"Failed to rotate file {filepath}: {e}")



    def is_valid_filename(self, filename):
        """
        Validates if a detected string is likely a real filename.
        """
        filename = filename.strip()
        
        # 1. Basic Length/Content check
        if len(filename) < 2: return False
        if ' ' in filename: return False
        
        # 2. Block Bad Prefixes (underscore often implies internal code ref, not file)
        if filename.startswith('_'): return False
        
        # 3. Stopwords
        stopwords = {'directory', 'folder', 'file', 'code', 'here', 'script', 'example'}
        if filename.lower() in stopwords: return False
        
        # 4. Extension Requirement
        # If no extension, MUST be in allowlist
        _, ext = os.path.splitext(filename)
        if not ext:
            allowlist = {
                'makefile', 'dockerfile', 'jenkinsfile', 'vagrantfile', 
                'readme', 'license', 'changelog', 'notice', 'procfile', 'gemfile'
            }
            if filename.lower() not in allowlist:
                return False
                
        return True

    def sanitize_filename(self, filename):
        """
        Sanitizes the filename by removing invalid characters.
        """
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Collapse whitespace
        filename = re.sub(r'\s+', '_', filename)
        return filename.strip()


    def _write_file(self, directory, filename, content, language):
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Sanitize filename
        filename = self.sanitize_filename(os.path.basename(filename))
        
        # Infer extension if missing
        root, ext = os.path.splitext(filename)
        if not ext and language:
            normalized_lang = language.lower().strip()
            # Use the raw language tag as the extension
            filename = f"{filename}.{normalized_lang}"

        output_path = os.path.join(directory, filename)

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content) # Write CLEAN content, no headers
            print(f"Extracted: {output_path}")
            return output_path
        except Exception as e:
            print(f"Failed to write {output_path}: {e}")
            return output_path # Return best guess for manifest even on error?


    def _save_content_safely(self, dest_path, content, version_dict):
        """
        Helper to write content to dest_path, handling headers, version rotation,
        and parent directory creation.
        """
        try:
            # Check if file exists
            if os.path.exists(dest_path):
                # Check for Identical Content to prevent spam
                try:
                    with open(dest_path, 'r', encoding='utf-8') as current_f:
                        existing_content = current_f.read()
                    if existing_content == content:
                        print(f"Skipping identical file: {dest_path}")
                        return
                except Exception:
                    # If read fails, proceed to rotate just in case
                    pass

                # Rotate!
                # We use the full path as key to avoid collisions between files/foo.py and reconstructed/foo.py if they share a dict
                key = dest_path 
                
                current_v = version_dict.get(key, 1)
                self.rotate_file(dest_path, current_v)
                version_dict[key] = current_v + 1
            
            # Write new content
            if content:
                # Ensure validation of directory existence
                parent_dir = os.path.dirname(dest_path)
                if not os.path.exists(parent_dir):
                    os.makedirs(parent_dir)

                with open(dest_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Populated file: {dest_path}")
            else:
                print(f"Skipping empty content for {dest_path}")

        except Exception as e:
            print(f"Failed to populate {dest_path}: {e}")


    def merge_reconstruction(self, manifest_path, merge_target, clean_target=False):
        """
        Consolidates textually reconstructed files into a single unified directory.
        Last-write-wins strategy based on manifest order.
        
        :param clean_target: If True, deletes the merge_target directory before merging.
        """
        import json
        import shutil

        if not os.path.exists(manifest_path):
            print(f"Merge skipped: Manifest not found at {manifest_path}")
            return

        with open(manifest_path, 'r') as f:
            manifest = json.load(f)

        if clean_target and os.path.exists(merge_target):
            print(f"Cleaning merge target: {merge_target}")
            shutil.rmtree(merge_target)

        if not os.path.exists(merge_target):
            os.makedirs(merge_target)
            print(f"Created merge target directory: {merge_target}")

        count = 0
        
        # Determine the base directory of the current extraction to resolve relative paths
        base_extraction_dir = os.path.dirname(manifest_path)
        reconstructed_dir = os.path.join(base_extraction_dir, "reconstructed")

        print(f"Merging reconstruction into: {merge_target}")

        for entry in manifest:
            if "reconstructed_path" in entry:
                # 1. Get the source path (from reconstructed directory)
                rel_path = entry["reconstructed_path"]
                src_path = os.path.join(reconstructed_dir, rel_path)

                if os.path.exists(src_path):
                    # 2. Determine destination path
                    # User Request: Merged folder should house "sorted-by-type" folders.
                    # We prioritize 'sorted_path' from manifest.
                    
                    if "sorted_path" in entry:
                         dest_rel_path = entry["sorted_path"]
                    else:
                         # Fallback: Strip numbering from reconstructed path
                         # Regex to remove leading digits and underscore from first component?
                         # Or just use the reconstructed path as is (flattened slightly)
                         dest_rel_path = rel_path
                         parts = dest_rel_path.split(os.sep)
                         if len(parts) > 0:
                             parts[0] = re.sub(r'^\d{3}_', '', parts[0])
                         dest_rel_path = os.path.join(*parts)

                    dest_path = os.path.join(merge_target, dest_rel_path)
                    
                    # 3. Copy (Overwrite)
                    dest_dir = os.path.dirname(dest_path)
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)
                        
                    shutil.copy2(src_path, dest_path)
                    count += 1
 

        print(f"  -> Merged {count} files to {merge_target}")
