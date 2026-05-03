from django.http import request
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..forms import ProfileUpdateForm
from ..models import UserEmail

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
            
        # ... (keep your existing update_profile logic here) ...

    return render(request, 'profile.html', {'user': user})

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
