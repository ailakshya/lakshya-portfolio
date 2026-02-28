#!/usr/bin/env python3
"""
Convert markdown file to PDF using weasyprint
"""
import sys
import subprocess
from pathlib import Path

def convert_md_to_pdf(md_file, output_pdf):
    """Convert markdown to PDF using markdown + weasyprint"""
    
    # First, convert markdown to HTML
    md_content = Path(md_file).read_text()
    
    # Create HTML with enhanced styling
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 100%;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
            page-break-before: always;
        }}
        h1:first-of-type {{
            page-break-before: avoid;
        }}
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 8px;
            margin-top: 25px;
        }}
        h3 {{
            color: #555;
            margin-top: 20px;
        }}
        h4 {{
            color: #666;
            margin-top: 15px;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: "Courier New", monospace;
            font-size: 0.9em;
        }}
        pre {{
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            overflow-x: auto;
        }}
        pre code {{
            background-color: transparent;
            padding: 0;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 15px 0;
            padding: 10px 20px;
            background-color: #f9f9f9;
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
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        ul, ol {{
            margin: 10px 0;
            padding-left: 30px;
        }}
        li {{
            margin: 5px 0;
        }}
        hr {{
            border: none;
            border-top: 2px solid #e0e0e0;
            margin: 30px 0;
        }}
        .emoji {{
            font-size: 1.2em;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
'''
    
    # Convert markdown content - simple conversion
    import re
    
    # Escape HTML
    lines = md_content.split('\n')
    result_html = []
    in_code_block = False
    code_lang = ''
    
    for line in lines:
        # Code blocks
        if line.startswith('```'):
            if in_code_block:
                result_html.append('</code></pre>')
                in_code_block = False
            else:
                code_lang = line[3:].strip()
                result_html.append(f'<pre><code class="language-{code_lang}">')
                in_code_block = True
            continue
        
        if in_code_block:
            result_html.append(line)
            continue
        
        # Headers
        if line.startswith('# '):
            result_html.append(f'<h1>{line[2:]}</h1>')
        elif line.startswith('## '):
            result_html.append(f'<h2>{line[3:]}</h2>')
        elif line.startswith('### '):
            result_html.append(f'<h3>{line[4:]}</h3>')
        elif line.startswith('#### '):
            result_html.append(f'<h4>{line[5:]}</h4>')
        # Horizontal rules
        elif line.strip() == '---':
            result_html.append('<hr>')
        # Blockquotes
        elif line.startswith('> '):
            result_html.append(f'<blockquote>{line[2:]}</blockquote>')
        # Lists
        elif re.match(r'^\d+\.\s', line):
            match = re.match(r'^(\d+)\.\s(.+)$', line)
            if match:
                result_html.append(f'<ol start="{match.group(1)}"><li>{match.group(2)}</li></ol>')
        elif line.startswith('- ') or line.startswith('* '):
            result_html.append(f'<ul><li>{line[2:]}</li></ul>')
        # Tables
        elif '|' in line and not line.startswith('|:'):
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if all(c.replace('-', '').replace(':', '').strip() == '' for c in cells):
                continue  # Skip separator row
            if line.strip().startswith('|'):
                is_header = '**' in line or result_html and '<table>' not in ''.join(result_html[-5:])
                if is_header:
                    if '<table>' not in ''.join(result_html[-5:]):
                        result_html.append('<table>')
                    result_html.append('<tr>' + ''.join(f'<th>{c}</th>' for c in cells) + '</tr>')
                else:
                    result_html.append('<tr>' + ''.join(f'<td>{c}</td>' for c in cells) + '</tr>')
        # Empty lines
        elif line.strip() == '':
            result_html.append('<br>')
        # Regular paragraphs
        else:
            # Bold
            line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
            # Italic
            line = re.sub(r'\*(.+?)\*', r'<em>\1</em>', line)
            # Inline code
            line = re.sub(r'`(.+?)`', r'<code>\1</code>', line)
            result_html.append(f'<p>{line}</p>')
    
    html_content += '\n'.join(result_html)
    html_content += '''
</body>
</html>
'''
    
    # Save HTML
    html_file = Path(md_file).with_suffix('.html')
    html_file.write_text(html_content)
    print(f"✅ Created HTML: {html_file}")
    
    # Try to convert to PDF using weasyprint
    try:
        from weasyprint import HTML
        HTML(string=html_content).write_pdf(output_pdf)
        print(f"✅ Created PDF: {output_pdf}")
        return True
    except ImportError:
        print("❌ weasyprint not installed")
        print(f"📄 HTML file created at: {html_file}")
        print(f"\n💡 To create PDF, you can:")
        print(f"   1. Open {html_file} in your browser and print to PDF")
        print(f"   2. Install weasyprint: pip install weasyprint")
        print(f"   3. Or install pandoc: brew install pandoc")
        return False

if __name__ == '__main__':
    md_file = 'slide_by_slide_explanation.md'
    pdf_file = 'Slide_by_Slide_Presentation_Guide.pdf'
    
    convert_md_to_pdf(md_file, pdf_file)
