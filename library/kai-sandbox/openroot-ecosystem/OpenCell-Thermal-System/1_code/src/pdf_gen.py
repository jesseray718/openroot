from fpdf import FPDF
import re

def create_pdf(input_file, output_file):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Set wide margins for wrapping
    left_margin = 15
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: File not found!")
        return

    sections = [s.strip() for s in content.split('---') if s.strip()]
    
    for i, section in enumerate(sections):
        lines = section.split('\n')
        
        # Title Page
        if i == 0:
            pdf.add_page()
            pdf.set_font("Helvetica", 'B', 24)
            pdf.set_x(left_margin)
            pdf.cell(pdf.epw, 20, "Project Aero-Geodesic", ln=True, align='C')
            pdf.set_font("Helvetica", 'B', 14)
            pdf.set_x(left_margin)
            pdf.cell(pdf.epw, 10, "Conversation Record", ln=True, align='C')
            pdf.ln(10)
            pdf.set_font("Helvetica", size=11)
            pdf.set_x(left_margin)
            for line in lines:
                clean = line.replace('---', '').strip()
                if ':' in clean and len(clean) < 100:
                    pdf.cell(pdf.epw, 6, clean[:70] + ('...' if len(clean)>70 else ''), ln=True)
            pdf.ln(20)
            continue

        # Content Pages
        pdf.add_page()
        first_line = lines[0].strip()
        
        # Identify Headers
        keywords = ["USER INPUT", "AI RESPONSE", "UPDATE", "CONFIRMATION", "TECHNICAL", "SECTION"]
        is_header = any(k in first_line.upper() for k in keywords)
        
        if is_header:
            pdf.set_font("Helvetica", 'B', 14)
            pdf.set_text_color(0, 51, 102)
            pdf.set_x(left_margin)
            pdf.multi_cell(pdf.epw, 6, first_line[:80])
            pdf.ln(2)
            start = 1
        else:
            start = 0
        
        pdf.set_font("Helvetica", size=11)
        pdf.set_text_color(50, 50, 50)
        
        for j in range(start, len(lines)):
            line = lines[j].strip()
            if not line:
                continue
            
            # Clean line: remove control chars, ensure safe chars
            line = re.sub(r'[^\x20-\x7E\n\r]', '', line)
            
            # If line is super long, force-break at words
            if len(line) > 80:
                # Insert soft breaks every 75 chars at word boundaries
                chunks = []
                current_chunk = ""
                words = line.split()
                for word in words:
                    if len(current_chunk) + len(word) + 1 <= 75:
                        current_chunk += (" " if current_chunk else "") + word
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = word
                if current_chunk:
                    chunks.append(current_chunk)
                
                for chunk in chunks:
                    pdf.set_x(left_margin)
                    pdf.multi_cell(pdf.epw, 6, chunk)
            else:
                pdf.set_x(left_margin)
                pdf.multi_cell(pdf.epw, 6, line)

    pdf.output(output_file)
    print("SUCCESS: PDF created!")
    print("Open with: termux-open " + output_file)

if __name__ == "__main__":
    create_pdf('lumo1-dossied.txt', 'AeroGeodesic_Conversation_Record.pdf')
