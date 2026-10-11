from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 10, 'AeroCement Whitepaper', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def sanitize_text(text):
    # Replace problematic unicode chars with ASCII
    replacements = {
        '\u2192': '-->',    # Right arrow
        '\u2190': '<--',    # Left arrow
        '\u2248': '~',      # Approximately
        '\u00b0': 'deg',    # Degree symbol
        '\u00b2': '^2',     # Superscript 2
        '\u2122': '(TM)',   # Trademark
        '\u00a9': '(C)',    # Copyright
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def create_pdf():
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    try:
        with open('Whitepaper_Summary.txt', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: Whitepaper_Summary.txt not found.")
        return

    lines = content.split('\n')
    
    for line in lines:
        line = sanitize_text(line.strip())
        if not line:
            continue
            
        # Check for Section Headers
        if len(line) > 2 and line[0].isdigit() and '.' in line[:5]:
            pdf.add_page()
            pdf.set_font('helvetica', 'B', 16)
            pdf.set_text_color(0, 51, 102)
            pdf.multi_cell(0, 10, line)
            pdf.ln(2)
            pdf.set_font('helvetica', '', 12)
            pdf.set_text_color(0, 0, 0)
        elif line.startswith('TITLE:') or line.startswith('AUTHOR:'):
            continue
        else:
            pdf.set_font('helvetica', '', 11)
            pdf.multi_cell(0, 6, line)
            pdf.ln(1)

    filename = 'AeroCement_Whitepaper.pdf'
    pdf.output(filename)
    print(f"\n*** Success! Saved as {filename} ***")
    print(f"*** Run: termux-open {filename} ***")

if __name__ == "__main__":
    create_pdf()
