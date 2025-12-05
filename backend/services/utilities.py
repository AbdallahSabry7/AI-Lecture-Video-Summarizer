import os
from datetime import datetime
from fpdf import FPDF

# Define where you want to save downloads
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def save_summary_to_txt(summary_text, chunk_summaries, video_url):
    # Create a unique filename based on timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"summary_{timestamp}.txt"
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"LECTURE SUMMARY\n")
            f.write(f"Source: {video_url}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write("="*50 + "\n\n")
            
            f.write("--- EXECUTIVE SUMMARY ---\n")
            f.write(summary_text + "\n\n")
            
            f.write("--- KEY POINTS (DETAILED) ---\n")
            for i, chunk in enumerate(chunk_summaries, 1):
                f.write(f"{i}. {chunk}\n")
                
        print(f"Text file saved at: {filepath}")
        return filepath
    except Exception as e:
        print(f"Error saving text file: {e}")
        return None


def save_summary_to_pdf(summary_text, chunk_summaries, video_url):
    """
    Saves the summary to a formatted PDF.
    Returns the file path.
    """
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 15)
            self.cell(0, 10, 'AI Lecture Summary', 0, 1, 'C')
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    # Create PDF object
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Metadata
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(100, 100, 100) # Grey color
    pdf.multi_cell(0, 5, f"Source: {video_url}\nDate: {datetime.now().strftime('%Y-%m-%d')}")
    pdf.ln(5)

    # Section 1: Main Summary
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0) # Black
    pdf.cell(0, 10, "Executive Summary", 0, 1)
    
    pdf.set_font("Arial", size=11)
    # multi_cell handles text wrapping automatically
    # normalize text to latin-1 for FPDF or use a unicode font if needed
    safe_text = summary_text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 7, safe_text)
    pdf.ln(5)

    # Section 2: Detailed Points
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Detailed Notes", 0, 1)
    
    pdf.set_font("Arial", size=11)
    for i, chunk in enumerate(chunk_summaries, 1):
        clean_chunk = chunk.strip().encode('latin-1', 'replace').decode('latin-1')
        # Draw a bullet point
        pdf.multi_cell(0, 7, f"{i}. {clean_chunk}")
        pdf.ln(2)

    # Generate Filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"summary_{timestamp}.pdf"
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)
    
    try:
        pdf.output(filepath)
        print(f"PDF saved at: {filepath}")
        return filepath
    except Exception as e:
        print(f"Error saving PDF: {e}")
        return None