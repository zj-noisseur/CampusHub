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
from django.db import transaction

User = get_user_model()

def sign_up(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST) # Use whatever your form name is!
        if form.is_valid():
            try:
                with transaction.atomic():
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

                messages.success(request, 'Registration successful! Please check your email to activate your account.')
                return redirect('core:login')
            
            except Exception as e:
                messages.error(request, 'We could not send the activation email. Please try registering again later.')
            
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
    
def resend_activation(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # Check if they are actually a sleeping account
            if not user.is_active:
                # 1. Build a fresh activation email
                current_site = get_current_site(request)
                subject = 'New Activation Link for CampusHub'
                html_message = render_to_string('activation_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'protocol': request.scheme,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })
        
                # 2. Send it
                send_mail(
                    subject=subject, 
                    message="Please view this email in an HTML compatible client.", 
                    from_email=None, 
                    recipient_list=[user.email],
                    html_message=html_message 
                )
                
                messages.success(request, 'A fresh activation link has been sent to your email!')
                return redirect('core:login')
            else:
                # They are already active!
                messages.info(request, 'This account is already active. You can just log in!')
                return redirect('core:login')
                
        except User.DoesNotExist:
            # Security trick: We pretend it worked so hackers can't use this form to guess which emails are registered!
            messages.success(request, 'If an inactive account exists for that email, a new link was sent.')
            return redirect('core:login')

    # If it's a GET request, just show the form
    return render(request, 'resend_activation.html')