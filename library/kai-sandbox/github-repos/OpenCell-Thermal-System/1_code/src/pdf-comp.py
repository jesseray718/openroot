cat > /root/make_combined_pdf.py <<'PY'
import os, textwrap
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Find every .txt file in the root directory
txt_files = sorted([f for f in os.listdir('/') if f.endswith('.txt')])

output_path = '/root/Combined_Conversation.pdf'
c = canvas.Canvas(output_path, pagesize=letter)

margin = 40
line_h = 12
y = letter[1] - margin
wrapper = textwrap.TextWrapper(width=95)

for fname in txt_files:
    # Title for each file
    c.setFont('Helvetica-Bold', 12)
    for line in wrapper.wrap(f'--- {fname} ---'):
        if y < margin:
            c.showPage()
            y = letter[1] - margin
        c.drawString(margin, y, line)
        y -= line_h
    y -= line_h

    # File contents
    c.setFont('Helvetica', 10)
    with open(fname, 'r', encoding='utf-8', errors='ignore') as f:
        for raw in f:
            if raw.strip() == '':
                y -= line_h
                continue
            for line in wrapper.wrap(raw.rstrip()):
                if y < margin:
                    c.showPage()
                    y = letter[1] - margin
                c.drawString(margin, y, line)
                y -= line_h
            y -= line_h
    y -= line_h * 2   # space between files

c.save()
print('✅ PDF written to', output_path)
PY
