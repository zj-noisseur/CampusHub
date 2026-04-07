import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4

def generate_certificate_pdf(background_path, student_name, center_x, center_y, font_size=40, font_color="#000000"):
    # 1. Create a "virtual file" in RAM 
    buffer = io.BytesIO()
    
    # 2. Set up an exact A4 Landscape canvas (841.89 x 595.27 points)
    width, height = landscape(A4)
    p = canvas.Canvas(buffer, pagesize=(width, height))
    
    # 3. Draw the background image ONLY if one is provided
    if background_path:
        p.drawImage(background_path, 0, 0, width=width, height=height)
    
    # 4. Configure the font and color
    p.setFont("Helvetica-Bold", font_size)
    
    # 5. THE MATH: Calculate exactly where to start writing so the name is centered
    text_width = p.stringWidth(student_name, "Helvetica-Bold", font_size)
    start_x = center_x - (text_width / 2)
    
    # 6. Draw the text onto the canvas
    p.drawString(start_x, center_y, student_name)
    
    # 7. Save and close the virtual file
    p.showPage()
    p.save()
    buffer.seek(0) # Rewind the file so Django can read it from the top
    
    return buffer