#!/usr/bin/env python3
"""
Simple font test script to check which Korean fonts work with wkhtmltopdf
"""

import pdfkit

def test_fonts():
    """Test different Korean fonts to see which ones work."""
    
    fonts_to_test = [
        ('Malgun Gothic', 'Malgun Gothic'),
        ('맑은 고딕', '맑은 고딕'),
        ('Dotum', 'Dotum'),
        ('돋움', '돋움'),
        ('Gulim', 'Gulim'),
        ('굴림', '굴림'),
        ('Batang', 'Batang'),
        ('바탕', '바탕'),
        ('Microsoft YaHei', 'Microsoft YaHei'),
        ('Arial', 'Arial')
    ]
    
    for font_en, font_display in fonts_to_test:
        print(f"Testing font: {font_display}")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
            body {{
                font-family: '{font_en}', Arial, sans-serif;
                font-size: 14px;
                padding: 20px;
            }}
            </style>
        </head>
        <body>
            <h1>Font Test: {font_display}</h1>
            <p>한글 텍스트 테스트입니다.</p>
            <p>English text test.</p>
            <p>특수문자: !, @, #, $, %, ^, &, *, (, )</p>
            <p>숫자: 1234567890</p>
            <code>코드 블록 테스트</code>
        </body>
        </html>
        """
        
        try:
            output_file = f"font_test_{font_en.replace(' ', '_')}.pdf"
            options = {
                'page-size': 'A4',
                'encoding': "UTF-8",
                'enable-local-file-access': None
            }
            
            pdfkit.from_string(html_content, output_file, options=options)
            print(f"  ✅ Success: {output_file}")
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")

if __name__ == "__main__":
    print("Testing Korean fonts with wkhtmltopdf...")
    test_fonts()
    print("\nCheck the generated PDF files to see which fonts display Korean text correctly.")