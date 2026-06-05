from django.http import request
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.forms import ProfileUpdateForm
from core.models import Club, UserEmail, Membership
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

@login_required
def user_profile(request):
    user = request.user

    if request.method == 'POST':
        # --- ACTION: Add a new email ---
        if 'add_email' in request.POST:
            new_email = request.POST.get('new_email')
            # Make sure it's not empty and doesn't already exist
            if new_email and not UserEmail.objects.filter(email=new_email).exists() and user.email != new_email:
                UserEmail.objects.create(user=user, email=new_email)
                messages.success(request, f"Added {new_email} to your account!")
            else:
                messages.error(request, "Invalid email or email already in use.")
            return redirect('core:profile')

        # --- ACTION: Delete an email ---
        elif 'delete_email' in request.POST:
            email_id = request.POST.get('email_id')
            UserEmail.objects.filter(id=email_id, user=user).delete() # Only delete if it belongs to this user!
            messages.success(request, "Email removed successfully.")
            return redirect('core:profile')
            
        # --- ACTION: Update phone number ---
        elif 'update_phone' in request.POST:
            new_phone = request.POST.get('phone_number')
            user.phone_number = new_phone
            user.save()
            messages.success(request, "Phone number updated successfully!")
            return redirect('core:profile') 
        
        # --- ACTION: Change password ---
        elif 'change_password' in request.POST:
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if not user.check_password(old_password):
                messages.error(request, "Your current password was entered incorrectly.")
            elif new_password != confirm_password:
                messages.error(request, "Your new passwords do not match.")
            else:
                try:
                    validate_password(new_password, user)
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)  
                    messages.success(request, "Your password has been successfully updated.")
                except ValidationError as e:
                    for error in e.messages:
                        messages.error(request, error)
            return redirect('core:profile')

    my_memberships = Membership.objects.filter(
        user=user, 
        status__in=['ACTIVE', 'APPROVED']
    ).select_related('club')

    managed_clubs = Club.objects.filter(managers__user=user)

    context = {
        'user': user,
        'my_memberships': my_memberships,
        'managed_clubs': managed_clubs,
    }

    return render(request, 'profile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('core:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'edit_profile.html', {'form': form})
