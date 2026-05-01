from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..forms import ClaimClubForm

@login_required(login_url='/admin/login/')
def claim_club(request):
    """View for claiming a club"""
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

    return render(request, 'claim_club.html', {'form': form})
