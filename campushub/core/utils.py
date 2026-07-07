import io
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from PIL import Image

def generate_certificate_pdf(student_name, background_bytes, custom_x, custom_y, font_size=24, font_color="#000000", font_name="Helvetica-Bold", 
                             extra_text=None, extra_x=None, extra_y=None, extra_size=20, extra_color="#000000"):
    # 1. Create a "virtual file" in memory
    buffer = io.BytesIO()
    
    # 2. Get the ACTUAL width and height of the uploaded image
    img_buffer = io.BytesIO(background_bytes)
    with Image.open(img_buffer) as img:
        img_width, img_height = img.size
    
    # 3. Set the canvas to match the exact image size
    p = canvas.Canvas(buffer, pagesize=(img_width, img_height))
    
    # 4. Stamp the background (seek back so ReportLab can re-read the bytes)
    img_buffer.seek(0)
    p.drawImage(img_buffer, 0, 0, width=img_width, height=img_height)
    
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


import base64
from django.conf import settings

def get_fernet():
    try:
        from cryptography.fernet import Fernet
        # Derive a 32-byte key from settings.SECRET_KEY
        # Ensure it is exactly 32 bytes and urlsafe base64 encoded
        derived_key = settings.SECRET_KEY[:32].encode().ljust(32, b' ')
        key = base64.urlsafe_b64encode(derived_key)
        return Fernet(key)
    except ImportError:
        return None

def encrypt_val(val):
    if not val:
        return ""
    f = get_fernet()
    if f:
        return f.encrypt(val.encode()).decode()
    # Fallback to simple base64 if cryptography is not installed
    return base64.b64encode(val.encode()).decode()

def decrypt_val(val):
    if not val:
        return ""
    f = get_fernet()
    if f:
        try:
            return f.decrypt(val.encode()).decode()
        except Exception:
            pass
    try:
        return base64.b64decode(val.encode()).decode()
    except Exception:
        return val


def extract_ig_handle(url):
    if not url:
        return ""
    # Remove query parameters (e.g. ?igsh=...)
    url = url.split('?')[0]
    # Remove trailing slashes
    url = url.rstrip('/')
    # Split by slashes
    parts = url.split('/')
    if parts:
        # The last non-empty segment should be the handle
        return parts[-1]
    return ""