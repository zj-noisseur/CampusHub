from django.shortcuts import render, redirect
from ..forms import StudentRegistrationForm
from django.contrib import messages

def register_student(request):
    """View for student registration"""
    # If the user hits the "Submit" button:
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()  # This saves the new student to your database!
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('register')  # For now, just reload the page

    # If the user is just visiting the page for the first time:
    else:
        form = StudentRegistrationForm()

    # Send the form to the HTML template
    return render(request, 'authentication/register.html', {'form': form}) 