from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import textwrap

def create_pdf(input_file, output_file):
    doc = SimpleDocTemplate(output_file, pagesize=letter)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, leading=28, alignment=TA_CENTER, spaceAfter=30)
    header_style = ParagraphStyle('Header', parent=styles['Heading2'], fontSize=16, leading=20, spaceAfter=10, textColor='#003366')
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=11, leading=14, alignment=TA_JUSTIFY, leftIndent=15, rightIndent=15, spaceAfter=6)
    
    story = []
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ Error: File 'lumo1-dossied.txt' not found.")
        return

    sections = [s.strip() for s in content.split('---') if s.strip()]
    
    for i, section in enumerate(sections):
        lines = section.split('\n')
        
        if i == 0:
            story.append(Paragraph("Project Aero-Geodesic<br/>Conversation Record", title_style))
            story.append(Spacer(1, 40))
            meta_lines = [line for line in lines if ':' in line]
            for line in meta_lines:
                clean = line.replace("---", "").strip()
                if clean:
                    story.append(Paragraph(clean, body_style))
                    story.append(Spacer(1, 5))
            story.append(PageBreak())
            continue

        first_line = lines[0].strip()
        is_header = any(k in first_line.upper() for k in ["USER INPUT", "AI RESPONSE", "UPDATE", "CONFIRMATION", "TECHNICAL"])
        
        if is_header:
            clean_header = first_line.replace("---", "").strip()
            story.append(Paragraph(clean_header, header_style))
            story.append(Spacer(1, 6))
            start = 1
        else:
            start = 0
        
        for j in range(start, len(lines)):
            line = lines[j].strip()
            if not line: continue
            wrapped = textwrap.fill(line, width=72)
            story.append(Paragraph(wrapped.replace('\n', '<br/>'), body_style))
        
        story.append(Spacer(1, 15))
        story.append(PageBreak())

    doc.build(story)
    print(f"\n✅ SUCCESS: {output_file} created!")
    print("Run: termux-open AeroGeodesic_Conversation_Record.pdf")

if __name__ == "__main__":
    create_pdf('lumo1-dossied.txt', 'AeroGeodesic_Conversation_Record.pdf')
