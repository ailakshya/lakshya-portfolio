#!/usr/bin/env python3
"""
Combine markdown files and convert to PDF
"""
import subprocess
import sys
from pathlib import Path

def convert_md_to_pdf_via_html(md_file, pdf_file):
    """Convert markdown to PDF via HTML using system tools"""
    try:
        # Read markdown
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Create HTML with styling
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 5px;
        }}
        h3 {{
            color: #7f8c8d;
            margin-top: 20px;
        }}
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Monaco', 'Courier New', monospace;
        }}
        pre {{
            background: #f8f8f8;
            padding: 15px;
            border-left: 4px solid #3498db;
            overflow-x: auto;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin-left: 0;
            color: #555;
            font-style: italic;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        hr {{
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 30px 0;
        }}
        .emoji {{
            font-size: 1.2em;
        }}
    </style>
</head>
<body>
{md_content.replace('```', '<pre><code>').replace('```', '</code></pre>').replace('**', '<strong>').replace('**', '</strong>').replace('*', '<em>').replace('*', '</em>')}
</body>
</html>
"""
        
        # Save HTML
        html_file = md_file.replace('.md', '.html')
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Convert HTML to PDF using system print
        result = subprocess.run([
            'cupsfilter',
            html_file,
            '>',
            pdf_file
        ], capture_output=True, text=True)
        
        print(f"Converted {md_file} to HTML: {html_file}")
        return html_file
        
    except Exception as e:
        print(f"Error converting {md_file}: {e}")
        return None

if __name__ == "__main__":
    base_dir = Path("/Users/lakshya/M.Tech sem 2 reserch paper")
    
    # Convert markdown files to HTML first
    files_to_convert = [
        base_dir / "presentation_guide.md",
        base_dir / "slide_by_slide_explanation.md"
    ]
    
    html_files = []
    for md_file in files_to_convert:
        if md_file.exists():
            html_file = convert_md_to_pdf_via_html(md_file, str(md_file).replace('.md', '.pdf'))
            if html_file:
                html_files.append(html_file)
    
    print(f"\\nCreated {len(html_files)} HTML files")
    print("Next: Use your browser to print these HTML files to PDF manually")
    print("Or install pandoc: brew install pandoc")
