from django.shortcuts import render, redirect
from .forms import StudentRegistrationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from.forms import StudentRegistrationForm, ClaimClubForm, MembershipApplicationForm
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

@login_required(login_url='/admin/login/')
def apply_membership(request):
    if request.method == 'POST':
        form = MembershipApplicationForm(request.POST)
        if form.is_valid():
            # 1. Save the Membership
            membership = form.save(commit=False)
            membership.user = request.user
            membership.save()
            
            # 2. Update the User's Profile with the new info!
            request.user.student_id = form.cleaned_data['student_id']
            request.user.phone_number = form.cleaned_data['phone_number']
            request.user.save()

            messages.success(request, 'Application submitted successfully!')
            return redirect('apply_membership')
    else:
        # MAGIC TRICK: If the user already provided their ID/Phone in the past, pre-fill the form so they don't have to type it again!
        initial_data = {
            'student_name': request.user.student_name,
            'student_id': request.user.student_id,
            'phone_number': request.user.phone_number,
        }
        form = MembershipApplicationForm(initial=initial_data)

    return render(request, 'authentication/membership.html', {'form': form})