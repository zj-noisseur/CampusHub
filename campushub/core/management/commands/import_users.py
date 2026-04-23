import openpyxl
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import User

class Command(BaseCommand):
    help = 'Bulk import users from an Excel file'

    def add_arguments(self, parser):
        # This tells Django to expect a file path when we run the command
        parser.add_argument('file_path', type=str, help='Path to the .xlsx file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        
        try:
            # Open the Excel file
            workbook = openpyxl.load_workbook(file_path)
            sheet = workbook.active
            
            success_count = 0
            
            # Loop through the rows, skipping the header row (min_row=2)
            for row in sheet.iter_rows(min_row=2, values_only=True):
                email = row[0]
                student_name = row[1]
                password = row[2]
                
                # Check if the row has data (prevents crashing on empty rows)
                if email and student_name and password:
                    # Check if user already exists to prevent duplicate crashes
                    if not User.objects.filter(email=email).exists():
                        # We use create_user so it properly hashes the password!
                        User.objects.create_user(
                            email=email,
                            student_name=student_name,
                            password=str(password)
                        )
                        success_count += 1
                        self.stdout.write(self.style.SUCCESS(f'Created: {email}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Skipped (Already exists): {email}'))
                        
            self.stdout.write(self.style.SUCCESS(f'\nSuccessfully imported {success_count} users!'))
            
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Could not find file: {file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}'))