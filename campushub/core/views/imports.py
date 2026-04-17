from django.shortcuts import render
from django.http import HttpResponse
import csv

from ..models import Event, PreRegisteredAttendee, User

def import_attendees_csv(request, event_id):
    event = Event.objects.get(id=event_id)

    if request.method == 'POST':
        
        # STEP 1: They uploaded a file
        if 'csv_file' in request.FILES:
            csv_file = request.FILES.get('csv_file')
            if not csv_file.name.endswith('.csv'):
                return HttpResponse("Error: Please upload a .csv file.")

            file_data = csv_file.read().decode('utf-8')
            request.session['temp_csv_data'] = file_data
            
            reader = csv.reader(file_data.splitlines())
            headers = next(reader, []) 

            return render(request, 'map_csv_columns.html', {
                'event': event, 
                'headers': headers
            })

        # STEP 2: They submitted the column mapping
        elif 'name_column' in request.POST:
            file_data = request.session.get('temp_csv_data')
            if not file_data:
                return HttpResponse("Error: Session expired. Please upload the file again.")

            name_col = request.POST.get('name_column')
            email_col = request.POST.get('email_column')
            student_id_col = request.POST.get('student_id_column')
            
            reader = csv.DictReader(file_data.splitlines())
            
            for row in reader:
                name = row.get(name_col, 'Unknown').strip()    
                email = row.get(email_col, '').strip()  
                
                student_id = row.get(student_id_col, '').strip() if student_id_col else ''

                if email:
                    if not student_id and email.endswith('@student.mmu.edu.my'):
                        student_id = email.split('@')[0]

                    if student_id:
                        user_account, created = User.objects.get_or_create(
                            email=email,
                            defaults={
                                'username': student_id, 
                                'first_name': name,
                                'student_id': student_id
                            }
                        )
                        
                        if created:
                            user_account.set_password('MMUClub123!') 
                            user_account.save()

                        # SAVING TO: PreRegisteredAttendee
                        PreRegisteredAttendee.objects.get_or_create(event=event, user=user_account)
                    
                    else:
                        # SAVING TO: PreRegisteredAttendee
                        PreRegisteredAttendee.objects.get_or_create(
                            event=event, 
                            guest_email=email,
                            defaults={'guest_name': name}
                        )
            
            del request.session['temp_csv_data']
            return HttpResponse(f"Success! Imported into Pre-Registration for {event.title}.")
        
        # FAILSAFE: If a POST request happened but no file or mapping was found!
        return HttpResponse("Error: No file detected. Check your HTML form tag for enctype='multipart/form-data'.")

    # STEP 0: Show the initial upload form
    return render(request, 'upload_csv.html', {'event': event})