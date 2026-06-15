from django.shortcuts import render, redirect
from django.contrib import messages
from core.forms import StudentRegistrationForm
from django.contrib.auth import login, get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import send_mail

def sign_up(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST) # Use whatever your form name is!
        if form.is_valid():
            # 1. Pause the save to lock the account!
            user = form.save(commit=False)
            user.is_active = False 
            user.save()
            
            # 2. Build the activation email
            current_site = get_current_site(request)
            subject = 'Activate your CampusHub Account'
            html_message = render_to_string('activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'protocol': request.scheme,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            
            # 3. Send it 
            send_mail(
                subject=subject, 
                message="Please view this email in an HTML compatible client.", 
                from_email=None, 
                recipient_list=[user.email],
                html_message=html_message 
            )
            
            # 4. Send them to a "Check your email" screen
            return render(request, 'activation_sent.html')
    else:
        form = StudentRegistrationForm()
    return render(request, 'sign_up.html', {'form': form})

def activate_account(request, uidb64, token):
    User = get_user_model()
    try:
        # Decode the user ID from the URL
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Check if the user exists AND the token hasn't been tampered with
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'activation_complete.html')
    else:
        return render(request, 'activation_invalid.html')