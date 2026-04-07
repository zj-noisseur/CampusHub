from django.shortcuts import render
from django.http import FileResponse, HttpResponse
from .utils import generate_certificate_pdf
from .models import EventCertificate

def test_certificate(request):
    # 1. Ask the database for the first template it finds (the one you just uploaded!)
    template = EventCertificate.objects.first()
    
    # Safety check in case the database is empty
    if not template:
        return HttpResponse("No template found! Go upload one in the Admin panel.")
        
    # 2. Get the physical file path of the image
    # Note: ReportLab needs the local computer path (.path), not the web URL
    # WARNING: If your field is called something else (like 'background'), change 'template.image.path' below!
    bg_path = template.template_image.path
    
    # read the custom x and y
    target_x = template.name_center_x
    target_y = template.name_center_y
    size = template.font_size
    color = template.font_color

    # 3. Pass BOTH the name and the background path to the engine
    pdf_buffer = generate_certificate_pdf(
        student_name="Zi Feng", 
        background_path=bg_path,
        custom_x=target_x,
        custom_y=target_y
    )
    
    # 4. Send the final stamped PDF back to the web browser
    return FileResponse(pdf_buffer, as_attachment=False, filename='test_certificate.pdf')