#!/usr/bin/env python3
"""
Merge multiple markdown files and convert to PDF while preserving markdown styling.
This script combines all Chapter markdown files in order and converts to PDF.
"""

import os
import re
import glob
from pathlib import Path
import markdown
import pdfkit
from datetime import datetime
import platform

def get_chapter_files(directory):
    """Get all Chapter markdown files sorted by chapter number."""
    pattern = os.path.join(directory, "Chapter*.md")
    files = glob.glob(pattern)
    
    # Sort by chapter number
    def extract_chapter_number(filename):
        match = re.search(r'Chapter\s*(\d+)', filename)
        return int(match.group(1)) if match else 0
    
    return sorted(files, key=extract_chapter_number)

def merge_markdown_files(files, output_path):
    """Merge multiple markdown files into one."""
    merged_content = []
    
    # Add title page
    merged_content.append("# AFM Data Platform Development Tutorial")
    merged_content.append(f"\n**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    merged_content.append("\n---\n")
    
    for file_path in files:
        print(f"Processing: {os.path.basename(file_path)}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add file separator
        chapter_name = os.path.splitext(os.path.basename(file_path))[0]
        merged_content.append(f"\n\n<!-- {chapter_name} -->\n")
        merged_content.append(content)
        merged_content.append("\n\n---\n")
    
    # Write merged content
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(merged_content))
    
    print(f"Merged content saved to: {output_path}")
    return output_path

def replace_icons_with_text(content):
    """Replace common icons and emoji with text alternatives for PDF."""
    
    # Common icon replacements
    icon_replacements = {
        # Emoji to Unicode/Text
        '✅': '✓',
        '❌': '✗',
        '⚠️': '⚠',
        '📝': '[메모]',
        '📋': '[목록]',
        '🔍': '[검색]',
        '💡': '[팁]',
        '⭐': '★',
        '🚀': '[시작]',
        '📊': '[차트]',
        '🛠️': '[도구]',
        '📁': '[폴더]',
        '📄': '[문서]',
        '🔗': '[링크]',
        '💻': '[컴퓨터]',
        '🌐': '[웹]',
        
        # Font Awesome icons (if used)
        '<i class="fa fa-check"></i>': '✓',
        '<i class="fa fa-times"></i>': '✗',
        '<i class="fa fa-warning"></i>': '⚠',
        '<i class="fa fa-info"></i>': 'ℹ',
        '<i class="fa fa-home"></i>': '🏠',
        '<i class="fa fa-user"></i>': '👤',
        '<i class="fa fa-cog"></i>': '⚙',
        '<i class="fa fa-search"></i>': '🔍',
        
        # Material Design icons (if used)
        '<i class="material-icons">check</i>': '✓',
        '<i class="material-icons">close</i>': '✗',
        '<i class="material-icons">warning</i>': '⚠',
        '<i class="material-icons">info</i>': 'ℹ',
        '<i class="material-icons">home</i>': '🏠',
        '<i class="material-icons">settings</i>': '⚙',
        
        # Common HTML entities
        '&check;': '✓',
        '&cross;': '✗',
        '&warning;': '⚠',
        '&info;': 'ℹ',
        
        # Badge-like text
        '[badge]': '🏷',
        '[new]': '🆕',
        '[updated]': '🔄',
        '[deprecated]': '⚠ 지원중단',
        
        # Status indicators
        '[success]': '✓ 성공',
        '[error]': '✗ 오류',
        '[warning]': '⚠ 경고',
        '[info]': 'ℹ 정보',
    }
    
    # Apply replacements
    for icon, replacement in icon_replacements.items():
        content = content.replace(icon, replacement)
    
    # Handle generic icon patterns
    import re
    
    # Replace <i class="...">...</i> with [ICON: content]
    content = re.sub(r'<i[^>]*class="[^"]*"[^>]*>([^<]*)</i>', r'[ICON: \1]', content)
    
    # Replace empty icon tags with generic icon symbol
    content = re.sub(r'<i[^>]*class="[^"]*"[^>]*></i>', '🔸', content)
    
    return content

def markdown_to_pdf(md_file, pdf_file):
    """Convert markdown to PDF with styling."""
    
    # Read markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Replace icons with text alternatives
    md_content = replace_icons_with_text(md_content)
    
    # Convert markdown to HTML
    html = markdown.markdown(
        md_content,
        extensions=[
            'markdown.extensions.tables',
            'markdown.extensions.fenced_code',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc'
        ]
    )
    
    # Add CSS styling for better PDF appearance
    css_style = """
    <style>
    body {
        font-family: 'Malgun Gothic', '맑은 고딕', 'Noto Sans CJK KR', 'Noto Sans Korean', 'Dotum', '돋움', 'Gulim', '굴림', 'Batang', '바탕', 'Microsoft YaHei', Arial, sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50;
        margin-top: 2em;
        margin-bottom: 1em;
    }
    h1 {
        border-bottom: 3px solid #3498db;
        padding-bottom: 10px;
    }
    h2 {
        border-bottom: 2px solid #ecf0f1;
        padding-bottom: 5px;
    }
    code {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 3px;
        padding: 2px 4px;
        font-family: 'Consolas', 'Courier New', 'D2Coding', 'Nanum Gothic Coding', 'Malgun Gothic', '맑은 고딕', monospace;
    }
    pre {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 5px;
        padding: 15px;
        overflow-x: auto;
    }
    pre code {
        background: none;
        border: none;
        padding: 0;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 1em 0;
    }
    table th, table td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    table th {
        background-color: #f2f2f2;
        font-weight: bold;
    }
    blockquote {
        border-left: 4px solid #3498db;
        margin: 0;
        padding-left: 20px;
        color: #7f8c8d;
    }
    hr {
        border: none;
        height: 2px;
        background-color: #ecf0f1;
        margin: 2em 0;
    }
    </style>
    """
    
    # Create complete HTML document
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>AFM Data Platform Tutorial</title>
        {css_style}
    </head>
    <body>
        {html}
    </body>
    </html>
    """
    
    # PDF options for better formatting
    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'no-outline': None,
        'enable-local-file-access': None,
        'minimum-font-size': '12'
    }
    
    try:
        # Convert HTML to PDF
        pdfkit.from_string(html_content, pdf_file, options=options)
        print(f"PDF created successfully: {pdf_file}")
        return True
    except Exception as e:
        print(f"Error creating PDF: {e}")
        print("Note: Make sure wkhtmltopdf is installed and accessible")
        return False

def check_fonts():
    """Check available fonts on Windows system."""
    if platform.system() == 'Windows':
        try:
            import winreg
            font_list = []
            
            # Check registry for installed fonts
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts")
            
            for i in range(winreg.QueryInfoKey(key)[1]):
                font_name = winreg.EnumValue(key, i)[0]
                if any(korean in font_name.lower() for korean in ['malgun', '맑은', 'dotum', '돋움', 'gulim', '굴림', 'batang', '바탕']):
                    font_list.append(font_name)
            
            winreg.CloseKey(key)
            
            print("Available Korean fonts:")
            for font in font_list[:10]:  # Show first 10
                print(f"  - {font}")
                
        except Exception as e:
            print(f"Could not check fonts: {e}")
            print("Common Windows Korean fonts should include: Malgun Gothic, Dotum, Gulim, Batang")

def main():
    """Main function to merge markdown files and convert to PDF."""
    
    # Check available fonts
    print("=== Font Check ===")
    check_fonts()
    
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get all chapter files
    chapter_files = get_chapter_files(current_dir)
    
    if not chapter_files:
        print("No Chapter markdown files found in the current directory")
        return
    
    print(f"Found {len(chapter_files)} chapter files:")
    for file in chapter_files:
        print(f"  - {os.path.basename(file)}")
    
    # Define output paths
    merged_md_file = os.path.join(current_dir, "AFM_Tutorial_Merged.md")
    pdf_file = os.path.join(current_dir, "AFM_Tutorial_Complete.pdf")
    
    try:
        # Step 1: Merge markdown files
        print("\n=== Merging Markdown Files ===")
        merge_markdown_files(chapter_files, merged_md_file)
        
        # Step 2: Convert to PDF
        print("\n=== Converting to PDF ===")
        success = markdown_to_pdf(merged_md_file, pdf_file)
        
        if success:
            print(f"\n✅ Success! Complete tutorial saved as:")
            print(f"   Markdown: {merged_md_file}")
            print(f"   PDF: {pdf_file}")
        else:
            print(f"\n⚠️  Markdown file created but PDF conversion failed.")
            print(f"   Markdown: {merged_md_file}")
            print("\nTo create PDF manually, install wkhtmltopdf or use an online converter.")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    # Check dependencies
    try:
        import markdown
        import pdfkit
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Install with: pip install markdown pdfkit")
        print("Also install wkhtmltopdf: https://wkhtmltopdf.org/downloads.html")
        exit(1)
    
    main()