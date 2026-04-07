from django.shortcuts import render
from django.http import FileResponse
from .utils import generate_certificate_pdf

def test_certificate(request):
    # We are using None for the background_path right now so it just makes a white page
    pdf_buffer = generate_certificate_pdf(
        background_path=None, 
        student_name="Zi Feng", 
        center_x=421,  # Exact middle of A4 Landscape (X)
        center_y=297   # Exact middle of A4 Landscape (Y)
    )
    
    # Send the PDF directly to the web browser to view
    return FileResponse(pdf_buffer, as_attachment=False, filename='test_certificate.pdf')
