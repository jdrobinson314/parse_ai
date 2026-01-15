import os
import html
import markdown
import re

# Pre-compiled markdown converter
md = markdown.Markdown(extensions=['fenced_code', 'tables', 'nl2br'])

def generate_html(conversation_data, output_path):
    """
    Generates a rich HTML file from the conversation data.
    
    Args:
        conversation_data (dict): The parsed conversation data structure.
        output_path (str): The full path to save the HTML file.
    """
    
    css = """
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f4f9;
            color: #333;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: #fff;
            padding: 40px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            border-radius: 8px;
        }
        
        /* Pagination / Page Size Simulation for Screen */
        .page {
            max-width: 816px; /* Approx US Letter Width */
            margin: 0 auto;
            padding: 40px;
            background: white;
            min-height: 1056px; /* Approx US Letter Height */
            margin-bottom: 20px;
        }

        h1 { color: #2c3e50; text-align: center; border-bottom: 2px solid #eee; padding-bottom: 15px; }
        h2 { color: #34495e; border-left: 5px solid #3498db; padding-left: 10px; margin-top: 30px; }
        
        .role-model { color: #2980b9; }
        .role-user { color: #27ae60; }
        .role-system { color: #e67e22; }

        .metadata {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            padding: 15px;
            border-radius: 5px;
            font-size: 0.9em;
            margin-bottom: 30px;
        }

        /* Collapsible Thoughts */
        details.thought-box {
            background-color: #fcfcfc;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            margin: 20px auto;
            width: 80%; /* Requested 80% width */
            box-shadow: 0 2px 5px rgba(0,0,0,0.02);
        }

        details.thought-box summary {
            cursor: pointer;
            padding: 10px 15px;
            background-color: #f0f2f5;
            color: #555;
            font-weight: 500;
            user-select: none;
            outline: none;
            border-bottom: 1px solid transparent;
            transition: background 0.2s;
            border-radius: 6px 6px 6px 6px;
        }
        
        details.thought-box[open] summary {
            border-radius: 6px 6px 0 0;
            border-bottom: 1px solid #e0e0e0;
        }

        details.thought-box summary:hover {
            background-color: #e2e6ea;
        }

        .thought-content {
            padding: 15px 25px;
            font-style: italic;
            color: #555;
            text-align: justify; /* Requested Justification */
            font-family: 'Georgia', serif;
            font-size: 0.95em;
        }

        pre {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            font-family: 'Consolas', 'Monaco', monospace;
        }
        
        blockquote {
            background: #f1f1f1;
            border-left: 5px solid #ccc;
            margin: 1.5em 10px;
            padding: 0.5em 10px;
        }
        
        /* Print / PDF Specifics */
        @media print {
            body { background: white; }
            .container { box-shadow: none; max-width: 100%; padding: 0; }
            details.thought-box { display: block !important; } /* Ensure thoughts are expanded/visible */
            details.thought-box summary { display: none; } /* Hide the clickable summary button in print */
            .thought-content { display: block; border-top: none; }
            
            /* Enforce the 80% width logic even in print if possible, though PDF generator handles this better */
            .thought-box {
                width: 80%;
                margin-left: auto;
                margin-right: auto;
            }
        }
    </style>
    """

    # Build Content
    content = []
    
    # Header
    content.append(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Parsed Chat Log</title>
        {css}
    </head>
    <body>
    <div class="container">
        <h1>Conversation Log</h1>
    """)

    # Metadata
    if 'runSettings' in conversation_data:
        meta_html = "<div class='metadata'><strong>Run Settings:</strong><br>"
        for k, v in conversation_data['runSettings'].items():
            meta_html += f"{k}: {v}<br>"
        meta_html += "</div>"
        content.append(meta_html)

    # Chunks
    if 'chunkedPrompt' in conversation_data and 'chunks' in conversation_data['chunkedPrompt']:
        for chunk in conversation_data['chunkedPrompt']['chunks']:
            role = chunk.get('role', 'unknown').title()
            text = chunk.get('text', '')
            is_thought = chunk.get('isThought', False)
            
            # Use markdown library to convert text to HTML
            # We don't need to manually escape HTML or handle newlines if we use 'nl2br' extension
            safe_text = md.convert(text)

            
            role_class = f"role-{role.lower()}"
            
            if is_thought:
                block = f"""
                <details class="thought-box" open>
                    <summary>Thought Process ({role})</summary>
                    <div class="thought-content">
                        {safe_text}
                    </div>
                </details>
                """
            else:
                block = f"""
                <div class="chat-block">
                    <h2 class="{role_class}">{role}</h2>
                    <div class="message-content">
                        {safe_text}
                    </div>
                </div>
                """
            content.append(block)

    content.append("</div></body></html>")
    
    full_html = "\n".join(content)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        print(f"Generated HTML: {output_path}")
        return True
    except Exception as e:
        print(f"Error generating HTML: {e}")
        return False

def generate_html_from_markdown(markdown_content, output_path, title="Document", subtitle=None):
    """
    Generates a rich HTML file from a plain Markdown string.
    
    Args:
        markdown_content (str): The raw markdown content.
        output_path (str): The full path to save the HTML file.
        title (str): Document title.
        subtitle (str): Optional subtitle (e.g., file path).
    """
    
    # Re-using the CSS from generate_html (conceptually, we could refactor CSS to a constant)
    css = """
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f4f9;
            color: #333;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: #fff;
            padding: 40px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            border-radius: 8px;
        }
        .page {
            max-width: 816px;
            margin: 0 auto;
            padding: 40px;
            background: white;
            min-height: 1056px;
            margin-bottom: 20px;
        }
        h1 { color: #2c3e50; text-align: center; border-bottom: 2px solid #eee; padding-bottom: 15px; }
        h2 { color: #34495e; border-left: 5px solid #3498db; padding-left: 10px; margin-top: 30px; }
        pre {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            font-family: 'Consolas', 'Monaco', monospace;
        }
        blockquote {
            background: #f1f1f1;
            border-left: 5px solid #ccc;
            margin: 1.5em 10px;
            padding: 0.5em 10px;
        }
        
        /* File Info Header (Code Block Style) */
        .file-info-block {
            font-family: 'Consolas', 'Monaco', monospace;
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 10px 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            border: 1px solid #444;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .file-title { 
            font-weight: bold; 
            font-size: 1.1em; 
            border-bottom: 1px solid #555; 
            padding-bottom: 5px; 
            margin-bottom: 5px;
            line-height: 1.2;
        }
        .file-path { 
            font-size: 0.85em; 
            color: #aaa; 
            line-height: 1.2;
        }

        @media print {
            body { background: white; }
            .container { box-shadow: none; max-width: 100%; padding: 0; }
            .file-info-block { background: #eee; color: #333; border: 1px solid #ccc; }
            .file-title { border-bottom: 1px solid #ccc; }
            .file-path { color: #555; }
        }
    </style>
    """
    
    # Convert Markdown to HTML
    html_content = md.convert(markdown_content)
    
    # Determine Header Logic
    if subtitle:
        header_html = f"""
        <div class="file-info-block">
            <div class="file-title">{title}</div>
            <div class="file-path">{subtitle}</div>
        </div>
        """
    else:
        header_html = f"<h1>{title}</h1>"
    
    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        {css}
    </head>
    <body>
    <div class="container">
        {header_html}
        {html_content}
    </div>
    </body>
    </html>
    """
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        print(f"Generated HTML (from MD): {output_path}")
        return True
    except Exception as e:
        print(f"Error generating HTML from MD: {e}")
        return False
