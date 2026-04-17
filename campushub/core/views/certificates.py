from django.shortcuts import get_object_or_404
from django.http import FileResponse, HttpResponse
from django.contrib.auth.decorators import login_required
import zipfile
import io

from ..models import Event, EventCertificate, Attendance
from ..utils import generate_certificate_pdf

def download_certificates(request, event_id):
    event = Event.objects.get(id=event_id)
    template = EventCertificate.objects.filter(event=event).first()
    
    if not template:
        return HttpResponse(f"No certificate template uploaded for {event.title} yet!")
    
    # Notice we added 'attended=True' here based on your earlier request!
    attendees = Attendance.objects.filter(event=event)
    if not attendees.exists():
        return HttpResponse("No attendees found for this event!")

    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for person in attendees:
            if person.guest_name:
                student_name = person.guest_name
            elif person.user:
                student_name = person.user.first_name if person.user.first_name else person.user.username
            else:
                student_name = "Unknown_Attendee"
            
            pdf_buffer = generate_certificate_pdf(
                student_name=student_name, 
                background_path=template.template_image.path,
                custom_x=template.name_center_x,
                custom_y=template.name_center_y,
                font_size=template.font_size,
                font_color=template.font_color
            )
            
            filename = f"{student_name}_Certificate.pdf"
            zip_file.writestr(filename, pdf_buffer.getvalue())

    zip_buffer.seek(0)
    zip_filename = f"{event.title}_Certificates.zip"
    return FileResponse(zip_buffer, as_attachment=True, filename=zip_filename)

@login_required
def download_my_certificate(request, attendance_id):
    attendance = get_object_or_404(Attendance, id=attendance_id, user=request.user)
    event = attendance.event
    
    template = EventCertificate.objects.filter(event=event).first()
    if not template:
        return HttpResponse(f"No certificate template uploaded for {event.title} yet!")
        
    student_name = attendance.guest_name if attendance.guest_name else request.user.first_name
        
    pdf_buffer = generate_certificate_pdf(
        student_name=student_name,
        background_path=template.template_image.path,
        custom_x=template.name_center_x,
        custom_y=template.name_center_y,
        font_size=template.font_size,
        font_color=template.font_color
    )
    
    pdf_buffer.seek(0)
    filename = f"{student_name}_{event.title}_Certificate.pdf"
    
    return FileResponse(pdf_buffer, as_attachment=True, filename=filename)