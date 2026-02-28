#!/usr/bin/env python3
"""
Convert markdown to PDF using reportlab
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import re
from pathlib import Path

def markdown_to_pdf(md_file, pdf_file):
    """Convert markdown to PDF"""
    
    # Read markdown content
    content = Path(md_file).read_text()
    
    # Create PDF
    pdf = SimpleDocTemplate(
        pdf_file,
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=20,
        borderPadding=5
    )
    
    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=10,
        spaceBefore=15
    )
    
    h3_style = ParagraphStyle(
        'CustomH3',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#555555'),
        spaceAfter=8,
        spaceBefore=12
    )
    
    h4_style = ParagraphStyle(
        'CustomH4',
        parent=styles['Heading4'],
        fontSize=12,
        textColor=colors.HexColor('#666666'),
        spaceAfter=6,
        spaceBefore=10
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        spaceAfter=6
    )
    
    quote_style = ParagraphStyle(
        'CustomQuote',
        parent=styles['BodyText'],
        fontSize=10,
        leftIndent=20,
        rightIndent=20,
        textColor=colors.HexColor('#555555'),
        backColor=colors.HexColor('#f9f9f9'),
        borderColor=colors.HexColor('#3498db'),
        borderWidth=2,
        borderPadding=10,
        spaceAfter=10
    )
    
    code_style = ParagraphStyle(
        'CustomCode',
        parent=styles['Code'],
        fontSize=9,
        leftIndent=20,
        backColor=colors.HexColor('#f8f8f8'),
        borderColor=colors.HexColor('#dddddd'),
        borderWidth=1,
        borderPadding=10,
        fontName='Courier'
    )
    
    # Story (content)
    story = []
    
    lines = content.split('\n')
    i = 0
    is_first_h1 = True
    
    while i < len(lines):
        line = lines[i].rstrip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
        
        # Headers
        if line.startswith('# '):
            if is_first_h1:
                story.append(Paragraph(line[2:], title_style))
                is_first_h1 = False
            else:
                story.append(PageBreak())
                story.append(Paragraph(line[2:], h1_style))
        elif line.startswith('## '):
            story.append(Paragraph(line[3:], h2_style))
        elif line.startswith('### '):
            story.append(Paragraph(line[4:], h3_style))
        elif line.startswith('#### '):
            story.append(Paragraph(line[5:], h4_style))
        
        # Horizontal rule
        elif line.strip() == '---':
            story.append(Spacer(1, 0.2*inch))
        
        # Blockquote
        elif line.startswith('> '):
            quote_text = line[2:]
            # Collect multi-line quotes
            while i + 1 < len(lines) and lines[i + 1].startswith('> '):
                i += 1
                quote_text += '<br/>' + lines[i][2:]
            story.append(Paragraph(quote_text, quote_style))
        
        # Code blocks
        elif line.startswith('```'):
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].startswith('```'):
                code_lines.append(lines[i])
                i += 1
            if code_lines:
                code_text = '<br/>'.join(code_lines)
                story.append(Paragraph(code_text, code_style))
        
        # Lists
        elif re.match(r'^\d+\.\s', line) or line.startswith('- ') or line.startswith('* '):
            list_items = []
            indent_level = 0
            
            while i < len(lines):
                curr_line = lines[i].rstrip()
                if not curr_line:
                    break
                
                # Numbered list
                if re.match(r'^\d+\.\s', curr_line):
                    text = re.sub(r'^\d+\.\s', '• ', curr_line)
                    list_items.append(text)
                # Bullet list
                elif curr_line.startswith('- ') or curr_line.startswith('* '):
                    list_items.append('• ' + curr_line[2:])
                # Indented item
                elif curr_line.startswith('  - ') or curr_line.startswith('  * '):
                    list_items.append('  ◦ ' + curr_line[4:])
                else:
                    break
                i += 1
            
            for item in list_items:
                # Clean markdown formatting
                item = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', item)
                item = re.sub(r'\*(.+?)\*', r'<i>\1</i>', item)
                item = re.sub(r'`(.+?)`', r'<font name="Courier">\1</font>', item)
                story.append(Paragraph(item, body_style))
            
            i -= 1  # Adjust because we'll increment at the end
        
        # Tables (simple support)
        elif '|' in line and line.strip().startswith('|'):
            table_data = []
            while i < len(lines) and '|' in lines[i]:
                curr_line = lines[i].strip()
                if curr_line.startswith('|:') or curr_line.startswith('|-'):
                    i += 1
                    continue
                cells = [c.strip() for c in curr_line.split('|')[1:-1]]
                if cells:
                    table_data.append(cells)
                i += 1
            
            if table_data:
                t = Table(table_data)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
                ]))
                story.append(t)
                story.append(Spacer(1, 0.2*inch))
            i -= 1
        
        # Regular paragraph
        else:
            text = line
            # Clean markdown formatting
            text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
            text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
            text = re.sub(r'`(.+?)`', r'<font name="Courier">\1</font>', text)
            
            if text.strip():
                story.append(Paragraph(text, body_style))
        
        i += 1
    
    # Build PDF
    pdf.build(story)
    print(f"✅ PDF created successfully: {pdf_file}")
    return True

if __name__ == '__main__':
    try:
        markdown_to_pdf(
            'slide_by_slide_explanation.md',
            'Slide_by_Slide_Presentation_Guide.pdf'
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
