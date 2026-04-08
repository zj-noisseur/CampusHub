from django.shortcuts import render
import zipfile
import csv
import io
from django.shortcuts import render, get_object_or_404
from django.http import FileResponse, HttpResponse
from django.db.models import Count
from .utils import generate_certificate_pdf
from .models import Event, EventCertificate, Attendance 
from django.contrib.auth.decorators import login_required

# --- 1. THE NEW DASHBOARD VIEW ---
def event_dashboard(request):
    # Ask the database for all events, and count how many attendees each one has!
    events = Event.objects.annotate(attendee_count=Count('attendances'))
    
    # Send this data to a new HTML page
    return render(request, 'core/dashboard.html', {'events': events})


def download_certificates(request, event_id):
    # Find the specific event they clicked on
    event = Event.objects.get(id=event_id)
    
    # Find the template for THAT specific event
    template = EventCertificate.objects.filter(event=event).first()
    if not template:
        return HttpResponse(f"No certificate template uploaded for {event.title} yet!")
    
    attendees = Attendance.objects.filter(event=event)
    if not attendees.exists():
        return HttpResponse("No attendees found for this event!")

    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for person in attendees:
            # 1. Prioritize the custom guest name
            if person.guest_name:
                student_name = person.guest_name
            # 2. Fall back to registered user
            elif person.user:
                student_name = person.user.username
            # 3. Safety fallback
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

def import_attendees_csv(request, event_id):
    # 1. Grab the event we are uploading to
    event = Event.objects.get(id=event_id)

    if request.method == 'POST':
        # 2. Get the uploaded file
        csv_file = request.FILES.get('csv_file')
        
        # Safety check: Did they actually upload a CSV?
        if not csv_file or not csv_file.name.endswith('.csv'):
            return HttpResponse("Error: Please upload a .csv file.")

        # 3. Read the file data
        file_data = csv_file.read().decode('utf-8').splitlines()
        reader = csv.reader(file_data)
        
        # Skip the header row (e.g., "Timestamp, Name, Email")
        next(reader, None)

        # 4. Loop through the rows and create attendees!
        for row in reader:
            # Assuming Column A (row[0]) is Name and Column B (row[1]) is Email
            if len(row) >= 2:
                guest_name = row[0].strip()
                guest_email = row[1].strip()
                
                # Create the record in the database
                Attendance.objects.create(
                    event=event,
                    guest_name=guest_name,
                    guest_email=guest_email
                )
                
        return HttpResponse(f"Success! Imported attendees into {event.title}.")

    # If they haven't uploaded anything yet, show them the upload form
    return render(request, 'core/upload_csv.html', {'event': event})


def club_admin_dashboard(request):
    # Grab all events (Later, you can filter this so they only see their own club's events!)
    events = Event.objects.all()
    # Notice we renamed the HTML file it points to!
    return render(request, 'core/club_admin_dashboard.html', {'events': events})

@login_required # Forces them to log in to see their personal certificates
def student_dashboard(request):
    # Find every event this specific user attended
    my_attendances = Attendance.objects.filter(user=request.user)
    
    return render(request, 'core/student_dashboard.html', {'attendances': my_attendances})

@login_required
def download_my_certificate(request, attendance_id):
    attendance = get_object_or_404(Attendance, id=attendance_id, user=request.user)
    event = attendance.event
    
    template = EventCertificate.objects.filter(event=event).first()
    if not template:
        return HttpResponse(f"No certificate template uploaded for {event.title} yet!")
        
    student_name = attendance.guest_name if attendance.guest_name else request.user.username
        
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
