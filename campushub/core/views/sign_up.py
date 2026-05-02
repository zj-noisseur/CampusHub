from django.shortcuts import render, redirect
from django.contrib import messages
from ..forms import StudentRegistrationForm
from django.contrib.auth import login

def sign_up(request):
    """View for student registration"""
    # If the user hits the "Submit" button:
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # This saves the new student to your database!
            login(request, user, backend= "django.contrib.auth.backends.ModelBackend")  # Log the user in automatically
            messages.success(request, 'Account created successfully! Welcome to CampusHub!')
            return redirect('profile')  # Redirect to profile page after successful registration

    # If the user is just visiting the page for the first time:
    else:
        form = StudentRegistrationForm()

    # Send the form to the HTML template
    
    return render(request, 'core/sign_up.html', {'form': form})
