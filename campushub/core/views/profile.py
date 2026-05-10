from django.http import request
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.forms import ProfileUpdateForm
from core.models import Club, UserEmail, Membership

@login_required
def user_profile(request):
    user = request.user

    if request.method == 'POST':
        if 'add_email' in request.POST:
            new_email = request.POST.get('new_email')

            if new_email and not UserEmail.objects.filter(email=new_email).exists() and user.email != new_email:
                UserEmail.objects.create(user=user, email=new_email)
                messages.success(request, f"Added {new_email} to your account!")
            else:
                messages.error(request, "Invalid email or email already in use.")
            return redirect('core:profile')

        elif 'delete_email' in request.POST:
            email_id = request.POST.get('email_id')
            UserEmail.objects.filter(id=email_id, user=user).delete() 
            messages.success(request, "Email removed successfully.")
            return redirect('core:profile')
        
        elif 'update_phone' in request.POST:
            new_phone = request.POST.get('phone_number')
            
            user.phone_number = new_phone
            user.save()
            
            messages.success(request, "Phone number updated successfully!")
            return redirect('core:profile') 
            
    my_memberships = Membership.objects.filter(
        user=user, 
        status='APPROVED'
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
