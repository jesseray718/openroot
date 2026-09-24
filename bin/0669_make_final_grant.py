#!/data/data/com.termux/files/usr/bin/python3
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
import os

def create_pdf():
    input_path = "/data/data/com.termux/files/home/AERO_ROOT/99-INBOX/downloads/MASTER_CONTEXT_ANCHOR_v2.txt"
    output_path = "/sdcard/Download/AeroCement_Final.pdf"

    print(f"Reading: {input_path}")

    if not os.path.exists(input_path):
        print("ERROR: Source file not found.")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    doc = SimpleDocTemplate(output_path, pagesize=letter,
                            rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    story = []

    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("AEROCENT ECOSYSTEM PROPOSAL", styles["Title"]))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Principal Investigator: Jesse McMillen", styles["Normal"]))
    story.append(Paragraph("June 2026 | Status: Patent Pending", styles["Normal"]))
    story.append(PageBreak())

    for line in lines:
        s = line.strip()
        if not s:
            story.append(Spacer(1, 6))
        elif s.startswith("##"):
            story.append(Paragraph(s.replace("##","").strip(), styles["Heading2"]))
        elif s.startswith("#"):
            story.append(Paragraph(s.replace("#","").strip(), styles["Heading1"]))
        elif s.startswith("- ") or s.startswith("* "):
            story.append(Paragraph("• " + s.lstrip("-* "), styles["Normal"]))
        else:
            story.append(Paragraph(s, styles["Normal"]))

    try:
        doc.build(story)
        print(f"SUCCESS! PDF saved to: {output_path}")
    except Exception as e:
        print(f"PDF error: {e}")

if __name__ == "__main__":
    create_pdf()
