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
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to CampusHub.')
            return redirect('profile') #Redirect to home

    # If the user is just visiting the page for the first time:
    else:
        form = StudentRegistrationForm()

    # Send the form to the HTML template
    
    return render(request, 'core/sign_up.html', {'form': form})
