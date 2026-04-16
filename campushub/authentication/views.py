from django.shortcuts import render, redirect
from .forms import StudentRegistrationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from.forms import StudentRegistrationForm, ClaimClubForm
# Create your views here.
def register_student(request):
    # If the user hits the "Submit" button:
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save() # This saves the new student to your database!
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('register') # For now, just reload the page
    
    # If the user is just visiting the page for the first time:
    else:
        form = StudentRegistrationForm()

    # Send the form to the HTML template
    return render(request, 'authentication/register.html', {'form': form})

@login_required(login_url='/admin/login/') 
def claim_club(request):
    if request.method == 'POST':
        # request.FILES is required whenever your form accepts file uploads!
        form = ClaimClubForm(request.POST, request.FILES)
        if form.is_valid():
            # Don't save to the database just yet...
            claim_request = form.save(commit=False)
            
            # Attach the currently logged-in user to the request
            claim_request.user = request.user 
            
            # Now save it!
            claim_request.save()
            
            messages.success(request, 'Your proof has been submitted! An admin will review it shortly.')
            return redirect('claim_club')
    else:
        form = ClaimClubForm()

    return render(request, 'authentication/claim_club.html', {'form': form})