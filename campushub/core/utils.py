import io
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from PIL import Image

def generate_certificate_pdf(student_name, background_path, custom_x, custom_y, font_size=24, font_color="#000000"):
    # 1. Create a "virtual file" in memory
    buffer = io.BytesIO()
    
    # 2. Get the ACTUAL width and height of the uploaded image
    with Image.open(background_path) as img:
        img_width, img_height = img.size
    
    # 3. Set the canvas to match the exact image size
    p = canvas.Canvas(buffer, pagesize=(img_width, img_height))
    
    # 4. Stamp the background
    p.drawImage(background_path, 0, 0, width=img_width, height=img_height)
    
    # 5. Apply the custom font size and color from the database!
    p.setFont("Helvetica-Bold", font_size)
    p.setFillColor(HexColor(font_color)) # This reads hex codes like #FF0000
    
    # 6. Center the text EXACTLY on the X coordinate, using the new font size
    text_width = p.stringWidth(student_name, "Helvetica-Bold", font_size)
    start_x = custom_x - (text_width / 2)
    
    # 7. Draw the text
    p.drawString(start_x, custom_y, student_name)
    
    # 8. Save and rewind the file
    p.showPage()
    p.save()
    buffer.seek(0)
    
    return buffer