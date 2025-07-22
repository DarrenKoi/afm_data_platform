#!/usr/bin/env python3
"""
Convert markdown files to HTML while preserving fonts and styling.
Centers content and maintains original formatting.
"""

import os
import glob
import markdown
from pathlib import Path

def convert_md_to_html(md_file, output_dir=None):
    """Convert a single markdown file to HTML with styling."""
    
    # Read markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML with better code highlighting
    html_content = markdown.markdown(
        md_content,
        extensions=[
            'markdown.extensions.tables',
            'markdown.extensions.fenced_code',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc'
        ],
        extension_configs={
            'markdown.extensions.codehilite': {
                'css_class': 'highlight',
                'use_pygments': True,
                'noclasses': False,  # Use CSS classes for better control
                'linenos': False,
                'guess_lang': False  # Don't guess language to avoid Vue syntax errors
            }
        }
    )
    
    # CSS styling with centered layout
    css_style = """
    <style>
    body {
        font-family: 'Malgun Gothic', '맑은 고딕', 'Noto Sans CJK KR', 'Dotum', '돋움', 'Gulim', '굴림', Arial, sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 900px;
        margin: 0 auto;
        padding: 40px 20px;
        background-color: #fff;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50;
        margin-top: 2em;
        margin-bottom: 1em;
        text-align: left;
    }
    
    h1 {
        border-bottom: 3px solid #3498db;
        padding-bottom: 10px;
        text-align: center;
        margin-bottom: 2em;
    }
    
    h2 {
        border-bottom: 2px solid #ecf0f1;
        padding-bottom: 8px;
    }
    
    p {
        margin-bottom: 1em;
        text-align: justify;
    }
    
    code {
        background-color: #f1f3f4;
        border: 1px solid #e1e4e8;
        border-radius: 3px;
        padding: 2px 6px;
        font-family: 'Consolas', 'Monaco', 'Courier New', 'D2Coding', 'Nanum Gothic Coding', monospace;
        font-size: 0.9em;
        color: #24292e;
    }
    
    pre {
        background-color: #f6f8fa;
        border: 1px solid #e1e4e8;
        border-radius: 6px;
        padding: 16px;
        overflow-x: auto;
        margin: 1em 0;
        line-height: 1.45;
        font-family: 'Consolas', 'Monaco', 'Courier New', 'D2Coding', 'Nanum Gothic Coding', monospace;
    }
    
    pre code {
        background: none;
        border: none;
        padding: 0;
        color: inherit;
        font-size: 0.9em;
    }
    
    /* Enhanced syntax highlighting support */
    .highlight {
        background-color: #f6f8fa;
        border-radius: 6px;
        margin: 1em 0;
    }
    
    .highlight pre {
        background: none;
        border: none;
        margin: 0;
    }
    
    /* Fix Vue.js template syntax highlighting issues */
    .highlight .err {
        background: none !important;
        border: none !important;
        color: #24292e !important;
    }
    
    /* Override error highlighting for Vue directives */
    .highlight .nt {
        color: #22863a;
    }
    
    .highlight .na {
        color: #6f42c1;
    }
    
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 1.5em auto;
    }
    
    table th, table td {
        border: 1px solid #ddd;
        padding: 12px 8px;
        text-align: left;
    }
    
    table th {
        background-color: #f2f2f2;
        font-weight: bold;
        text-align: center;
    }
    
    blockquote {
        border-left: 4px solid #3498db;
        margin: 1em 0;
        padding-left: 20px;
        color: #7f8c8d;
        font-style: italic;
    }
    
    ul, ol {
        margin: 1em 0;
        padding-left: 2em;
    }
    
    li {
        margin-bottom: 0.5em;
    }
    
    hr {
        border: none;
        height: 2px;
        background-color: #ecf0f1;
        margin: 3em 0;
    }
    
    img {
        max-width: 100%;
        height: auto;
        display: block;
        margin: 1em auto;
        border-radius: 5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .highlight {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 10px;
        margin: 1em 0;
    }
    
    @media print {
        body {
            max-width: none;
            margin: 0;
            padding: 20px;
        }
    }
    </style>
    """
    
    # Get filename without extension
    base_name = os.path.splitext(os.path.basename(md_file))[0]
    
    # Create complete HTML document
    html_document = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{base_name}</title>
    {css_style}
</head>
<body>
    {html_content}
</body>
</html>"""
    
    # Determine output path
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{base_name}.html")
    else:
        output_file = os.path.join(os.path.dirname(md_file), f"{base_name}.html")
    
    # Write HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_document)
    
    print(f"✅ Converted: {os.path.basename(md_file)} → {os.path.basename(output_file)}")
    return output_file

def convert_all_chapters(directory=None, output_dir=None):
    """Convert all Chapter markdown files to HTML."""
    
    if directory is None:
        directory = os.path.dirname(os.path.abspath(__file__))
    
    # Find all Chapter markdown files
    pattern = os.path.join(directory, "Chapter*.md")
    md_files = glob.glob(pattern)
    
    if not md_files:
        print("No Chapter*.md files found in the directory")
        return
    
    # Sort files by chapter number
    def extract_chapter_number(filename):
        import re
        match = re.search(r'Chapter\s*(\d+)', filename)
        return int(match.group(1)) if match else 0
    
    md_files.sort(key=extract_chapter_number)
    
    print(f"Found {len(md_files)} chapter files to convert:")
    
    converted_files = []
    for md_file in md_files:
        try:
            html_file = convert_md_to_html(md_file, output_dir)
            converted_files.append(html_file)
        except Exception as e:
            print(f"❌ Error converting {os.path.basename(md_file)}: {e}")
    
    print(f"\n✅ Successfully converted {len(converted_files)} files")
    
    if output_dir:
        print(f"📁 Output directory: {output_dir}")
    
    return converted_files

def main():
    """Main function."""
    import sys
    
    if len(sys.argv) > 1:
        # Convert specific file
        input_file = sys.argv[1]
        if os.path.exists(input_file) and input_file.endswith('.md'):
            output_dir = sys.argv[2] if len(sys.argv) > 2 else None
            convert_md_to_html(input_file, output_dir)
        else:
            print(f"File not found or not a markdown file: {input_file}")
    else:
        # Convert all Chapter files in current directory
        output_dir = "html_output"
        print("Converting all Chapter*.md files to HTML...")
        convert_all_chapters(output_dir=output_dir)

if __name__ == "__main__":
    # Check dependencies
    try:
        import markdown
    except ImportError:
        print("Missing required package: markdown")
        print("Install with: pip install markdown")
        exit(1)
    
    try:
        import pygments
    except ImportError:
        print("Warning: pygments not found - syntax highlighting will be basic")
        print("For better code highlighting, install with: pip install pygments")
    
    main()