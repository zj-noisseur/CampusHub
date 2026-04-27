from django.shortcuts import get_object_or_404
from django.http import FileResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import zipfile
import io

from ..models import Event, EventCertificate, Attendance, PreRegisteredAttendee
from ..utils import generate_certificate_pdf

def download_certificates(request, event_id):
    event = Event.objects.get(id=event_id)
    template = EventCertificate.objects.filter(event=event).first()
    
    if not template:
        return HttpResponse(f"No certificate template uploaded for {event.title} yet!")
    
    # STRICTLY READS FROM THE ATTENDANCE TABLE
    attendees = Attendance.objects.filter(event=event)
    
    if not attendees.exists():
        return HttpResponse("No one is in the Attendance database table yet! Mark someone as 'Present' first.")

    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for person in attendees:
            
            # 1. Get the name
            if person.user:
                student_name = person.user.first_name if person.user.first_name else person.user.username
                # Double check they are "Ready" so it doesn't print broken certificates
                prereg = PreRegisteredAttendee.objects.filter(event=event, user=person.user).first()
            elif person.guest_name:
                student_name = person.guest_name
                prereg = PreRegisteredAttendee.objects.filter(event=event, guest_email=person.guest_email).first()
            else:
                student_name = "Unknown_Attendee"
                prereg = None
                
            # If they are in the attendance list but missing data (Unready), skip printing
            if prereg and not prereg.is_ready:
                continue

            # 2. Generate PDF
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
def download_my_certificate(request, event_id):
    user = request.user
    
    # Find attendance by user account OR guest email
    attendance = Attendance.objects.filter(
        Q(event_id=event_id) & (Q(user=user) | Q(guest_email=user.email))
    ).first()
    
    if not attendance:
        return HttpResponse("Attendance record not found for this event.", status=404)
        
    event = attendance.event
    
    if event.status != 'FINISHED':
        return HttpResponse("Certificates are not yet available for this event.", status=403)
    
    template = EventCertificate.objects.filter(event=event).first()
    if not template:
        return HttpResponse(f"No certificate template uploaded for {event.title} yet!")
        
    # Determine the name to print on the certificate
    student_name = attendance.guest_name if attendance.guest_name else (user.first_name if user.first_name else user.username)
        
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