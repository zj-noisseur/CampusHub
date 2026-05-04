from django.shortcuts import render, redirect
from django.http import HttpResponse
import csv

from ..models import Event, PreRegisteredAttendee, User
from django.db import IntegrityError
from django.db.models import Q

def import_attendees_csv(request, event_id):
    event = Event.objects.get(id=event_id)

    if request.method == 'POST':
        
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

        elif 'name_col' in request.POST:
            file_data = request.session.get('temp_csv_data')
            if not file_data:
                return HttpResponse("Error: Session expired. Please upload the file again.")

            name_col = request.POST.get('name_col')
            email_col = request.POST.get('email_col')
            student_id_col = request.POST.get('student_id_col')
            
            reader = csv.DictReader(file_data.splitlines())
            
            for row in reader:
                name = row.get(name_col, 'Unknown').strip()    
                email = row.get(email_col, '').strip()  
                student_id = row.get(student_id_col, '').strip() if student_id_col else ''

                # SMART CHECK: Are all 3 required fields completely filled out?
                is_complete = bool(name and name != 'Unknown' and email and student_id)

                if email:
                    if not student_id and email.endswith('@student.mmu.edu.my'):
                        student_id = email.split('@')[0]
                        # Re-evaluate in case we just successfully grabbed the ID from the email
                        is_complete = bool(name and name != 'Unknown' and email and student_id)

                    if student_id:
                        try:
                            user_account, created = User.objects.get_or_create(
                                email=email,
                                defaults={
                                    'student_name': name,
                                    'student_id': student_id
                                }
                            )
                        except IntegrityError:
                            # If email wasn't found but student_id exists, look it up by student_id
                            user_account = User.objects.get(student_id=student_id)
                            created = False
                        
                        if created:
                            user_account.set_password('MMUClub123!') 
                            user_account.save()
                        else:
                            if name and name != 'Unknown':
                                user_account.student_name = name
                            if student_id:
                                user_account.student_id = student_id
                            user_account.save()

                        prereg, _ = PreRegisteredAttendee.objects.get_or_create(event=event, user=user_account)
                        # Saves the smart check result
                        prereg.is_ready = is_complete  
                        prereg.save()
                    
                    else:
                        prereg, _ = PreRegisteredAttendee.objects.get_or_create(
                            event=event, 
                            email=email,
                            defaults={'name': name}
                        )
                        # Missing Student ID, instantly Unready
                        prereg.is_ready = False  
                        prereg.save()
                    
                else:
                    prereg, _ = PreRegisteredAttendee.objects.get_or_create(
                        event=event, 
                        email='no-email@guest.com',
                        defaults={'name': name}
                    )
                    # Missing Email and ID, instantly Unready
                    prereg.is_ready = False  
                    prereg.save()
            
            request.session.pop('temp_csv_data', None)
            return redirect('core:event_admin_dashboard', club_id=event.club.id, event_id=event.id)
        
        return HttpResponse("Error: No file or mapping data detected.")

    return render(request, 'upload_csv.html', {'event': event})