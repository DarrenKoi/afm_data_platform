#!/usr/bin/env python3
"""
Test script to check how different icons render in PDF
"""

import pdfkit

def test_icons():
    """Test various icon types in PDF conversion."""
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
        body {
            font-family: 'Malgun Gothic', '맑은 고딕', Arial, sans-serif;
            font-size: 14px;
            padding: 20px;
            line-height: 1.6;
        }
        .icon-test {
            margin: 10px 0;
            padding: 5px;
            border: 1px solid #ddd;
        }
        </style>
    </head>
    <body>
        <h1>Icon Rendering Test</h1>
        
        <h2>1. Unicode Symbols (should work)</h2>
        <div class="icon-test">✓ Checkmark</div>
        <div class="icon-test">✗ Cross</div>
        <div class="icon-test">⚠ Warning</div>
        <div class="icon-test">ℹ Info</div>
        <div class="icon-test">★ Star</div>
        <div class="icon-test">⚙ Settings</div>
        <div class="icon-test">📝 Memo</div>
        
        <h2>2. Emoji (may not work)</h2>
        <div class="icon-test">✅ Check emoji</div>
        <div class="icon-test">❌ Cross emoji</div>
        <div class="icon-test">⚠️ Warning emoji</div>
        <div class="icon-test">💡 Lightbulb</div>
        <div class="icon-test">🚀 Rocket</div>
        <div class="icon-test">📊 Chart</div>
        
        <h2>3. HTML Entities</h2>
        <div class="icon-test">&check; HTML check</div>
        <div class="icon-test">&cross; HTML cross</div>
        <div class="icon-test">&hearts; Hearts</div>
        <div class="icon-test">&spades; Spades</div>
        
        <h2>4. Font Awesome (will be blank without font)</h2>
        <div class="icon-test"><i class="fa fa-check"></i> FA Check</div>
        <div class="icon-test"><i class="fa fa-times"></i> FA Times</div>
        <div class="icon-test"><i class="fa fa-home"></i> FA Home</div>
        
        <h2>5. Material Icons (will be blank without font)</h2>
        <div class="icon-test"><i class="material-icons">check</i> Material Check</div>
        <div class="icon-test"><i class="material-icons">close</i> Material Close</div>
        <div class="icon-test"><i class="material-icons">home</i> Material Home</div>
        
        <h2>6. Custom replacements</h2>
        <div class="icon-test">[성공] Success</div>
        <div class="icon-test">[오류] Error</div>
        <div class="icon-test">[경고] Warning</div>
        <div class="icon-test">[정보] Info</div>
        
    </body>
    </html>
    """
    
    try:
        options = {
            'page-size': 'A4',
            'encoding': "UTF-8",
            'enable-local-file-access': None
        }
        
        pdfkit.from_string(html_content, "icon_test_result.pdf", options=options)
        print("✅ Icon test PDF created: icon_test_result.pdf")
        print("Check the PDF to see which icon types render correctly.")
        
    except Exception as e:
        print(f"❌ Failed to create PDF: {e}")

if __name__ == "__main__":
    test_icons()