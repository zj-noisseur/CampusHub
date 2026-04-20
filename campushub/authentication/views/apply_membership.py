from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..forms import MembershipApplicationForm


@login_required(login_url='/admin/login/')
def apply_membership(request):
    """View for applying to club membership"""
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
