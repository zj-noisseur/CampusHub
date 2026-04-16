from django.shortcuts import render, get_object_or_404
from django.http import FileResponse, HttpResponse
from django.db.models import Count
from django.contrib.auth.decorators import login_required
import zipfile
import csv
import io

# 1. FIXED: Added 'User' to your imports so the CSV tool can find it!
from .models import Event, EventCertificate, Attendance, User 
from .utils import generate_certificate_pdf

# --- 1. THE NEW DASHBOARD VIEW ---
def event_dashboard(request):
    events = Event.objects.annotate(attendee_count=Count('attendances'))
    return render(request, 'core/dashboard.html', {'events': events})

def download_certificates(request, event_id):
    event = Event.objects.get(id=event_id)
    template = EventCertificate.objects.filter(event=event).first()
    
    if not template:
        return HttpResponse(f"No certificate template uploaded for {event.title} yet!")
    
    attendees = Attendance.objects.filter(event=event)
    if not attendees.exists():
        return HttpResponse("No attendees found for this event!")

    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for person in attendees:
            if person.guest_name:
                student_name = person.guest_name
            elif person.user:
                student_name = person.user.username
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
    event = Event.objects.get(id=event_id)

    if request.method == 'POST':
        
        # ==========================================
        # STEP 1: THEY UPLOADED THE FILE
        # ==========================================
        if 'csv_file' in request.FILES:
            csv_file = request.FILES.get('csv_file')
            
            if not csv_file.name.endswith('.csv'):
                return HttpResponse("Error: Please upload a .csv file.")

            # Read the file and save it to the user's browser session (temporary memory)
            file_data = csv_file.read().decode('utf-8')
            request.session['temp_csv_data'] = file_data
            
            # Read just the very first line to get the Column Headers
            reader = csv.reader(file_data.splitlines())
            headers = next(reader, []) 

            # Send them to the new "Mapping" screen
            return render(request, 'core/map_csv_columns.html', {
                'event': event, 
                'headers': headers
            })

        elif 'name_column' in request.POST:
            # Grab the file data back out of memory
            file_data = request.session.get('temp_csv_data')
            
            if not file_data:
                return HttpResponse("Error: Session expired. Please upload the file again.")

            # Find out which columns they selected from the dropdowns
            name_col = request.POST.get('name_column')
            email_col = request.POST.get('email_column')
            
            # Now we read the CSV using their custom column choices!
            reader = csv.DictReader(file_data.splitlines())
            
            for row in reader:
                name = row.get(name_col, 'Unknown')    
                email = row.get(email_col)  

                if email:
                    user_account = User.objects.filter(email=email).first()

                    if user_account:
                        Attendance.objects.get_or_create(event=event, user=user_account)
                    else:
                        Attendance.objects.get_or_create(
                            event=event, 
                            guest_email=email,
                            defaults={'guest_name': name}
                        )
            
            # Delete the file from memory so it doesn't slow down the server
            del request.session['temp_csv_data']
            return HttpResponse(f"Success! Mapped and imported attendees into {event.title}.")

    # STEP 0: Show the initial upload form if they haven't done anything yet
    return render(request, 'core/upload_csv.html', {'event': event})

def club_admin_dashboard(request):
    events = Event.objects.all()
    return render(request, 'core/club_admin_dashboard.html', {'events': events})

@login_required
def student_dashboard(request):
    my_attendances = Attendance.objects.filter(user=request.user)
    return render(request, 'core/student_dashboard.html', {'attendances': my_attendances})

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