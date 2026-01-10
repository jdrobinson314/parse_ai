import os
from xhtml2pdf import pisa

def generate_pdf(source_html_path, output_path, page_size="Letter"):
    """
    Generates a PDF from an HTML file using xhtml2pdf.
    
    Args:
        source_html_path (str): Path to the source HTML file.
        output_path (str): Path to save the PDF.
        page_size (str): Page size (formatted for CSS @page). e.g., "Letter", "A4".
    """
    
    # We need to inject the page size into the HTML style before converting
    # or rely on the HTML having it. xhtml2pdf supports @page.
    
    try:
        with open(source_html_path, "r", encoding="utf-8") as f:
            source_html = f.read()
            
        # Inject @page size if needed, or ensure CSS handles it.
        # xhtml2pdf specific CSS for page size:
        page_css = f"""
        <style>
            @page {{
                size: {page_size};
                margin: 1cm;
                @frame footer_frame {{
                    -pdf-frame-content: footerContent;
                    bottom: 0cm;
                    margin-left: 1cm;
                    margin-right: 1cm;
                    height: 1cm;
                }}
            }}
            /* Specific overrides for PDF rendering consistency */
            details.thought-box {{
                width: 80%;
                margin-left: 10%; /* Center it (10% + 80% + 10%) */
                margin-right: 10%;
                text-align: justify;
                background-color: #fcfcfc;
                border: 1px solid #ccc;
                padding: 10px;
                display: block; /* Ensure it's visible */
            }}
            
            /* Hide the summary element in PDF since it's not interactive */
            details.thought-box summary {{
                display: none;
            }}
            
            /* Make sure the content is visible */
            .thought-content {{
                display: block;
            }}
        </style>
        """
        
        # Insert CSS before closing head
        if "</head>" in source_html:
            final_html = source_html.replace("</head>", f"{page_css}</head>")
        else:
            final_html = f"{page_css}{source_html}"

        with open(output_path, "wb") as dest_file:
            pisa_status = pisa.CreatePDF(
                src=final_html,
                dest=dest_file
            )

        if pisa_status.err:
            print(f"Error generating PDF: {pisa_status.err}")
            return False
            
        print(f"Generated PDF: {output_path} (Size: {page_size})")
        return True
        
    except Exception as e:
        print(f"Exception generating PDF: {e}")
        return False
