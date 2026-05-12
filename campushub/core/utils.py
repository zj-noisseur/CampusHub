import io
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from PIL import Image

def generate_certificate_pdf(student_name, background_path, custom_x, custom_y, font_size=24, font_color="#000000", font_name="Helvetica-Bold", 
                             extra_text=None, extra_x=None, extra_y=None, extra_size=20, extra_color="#000000"):
    # 1. Create a "virtual file" in memory
    buffer = io.BytesIO()
    
    # 2. Get the ACTUAL width and height of the uploaded image
    with Image.open(background_path) as img:
        img_width, img_height = img.size
    
    # 3. Set the canvas to match the exact image size
    p = canvas.Canvas(buffer, pagesize=(img_width, img_height))
    
    # 4. Stamp the background
    p.drawImage(background_path, 0, 0, width=img_width, height=img_height)
    
    # 5. Draw Student Name
    p.setFont(font_name, font_size)
    p.setFillColor(HexColor(font_color))
    text_width = p.stringWidth(student_name, font_name, font_size)
    start_x = custom_x - (text_width / 2)
    p.drawString(start_x, custom_y, student_name)
    
    # 6. Draw Custom Extra Field (if provided)
    if extra_text:
        p.setFont(font_name, extra_size) # We use the same font but different size/color
        p.setFillColor(HexColor(extra_color))
        
        # Center custom text if coordinates provided
        if extra_x is not None and extra_y is not None:
            c_text_width = p.stringWidth(extra_text, font_name, extra_size)
            c_start_x = extra_x - (c_text_width / 2)
            p.drawString(c_start_x, extra_y, extra_text)
    
    # 7. Save and rewind the file
    p.showPage()
    p.save()
    buffer.seek(0)
    
    return buffer