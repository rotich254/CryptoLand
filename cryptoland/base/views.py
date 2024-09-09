import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.html import strip_tags
from .models import OTPModel
from .forms import RegisterForm
from django.contrib import messages

@login_required(login_url='login')
def index(request):
    return render(request, 'index.html')

def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if not user.is_active:
                messages.warning(request, 'Your account is not verified. Please verify your account.')
                # Resend the OTP
                otp = generate_otp()
                OTPModel.objects.filter(user=user).delete()  # Clear any previous OTPs
                OTPModel.objects.create(user=user, otp=otp)
                
                send_mail(
                    'Your OTP Code',
                    f'Your OTP code is {otp}. Please enter this to verify your account.',
                    'no-reply@yourdomain.com',
                    [user.email],
                    fail_silently=False,
                )
                
                return redirect('verify_otp', user_id=user.id)  # Redirect to OTP verification page
            else:
                login(request, user)
                messages.success(request, 'You have successfully logged in')
                return redirect('index')
        else:
            messages.error(request, 'Invalid username or password!')
    return render(request, 'login.html')



def generate_otp():
    return str(random.randint(10000, 9999999))

def registerPage(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.is_active = False  # User is inactive until they verify OTP
            user.save()

            otp = generate_otp()
            OTPModel.objects.create(user=user, otp=otp)

            send_mail(
                'Your OTP Code',
                f'Your OTP code is {otp}. Please enter this to verify your account.',
                'no-reply@yourdomain.com',
                [user.email],
                fail_silently=False,
            )

            messages.success(request, 'Registration successful! Please check your email for the OTP.')
            return redirect('verify_otp', user_id=user.id)
        else:
            for error in list(form.errors.values()):
                messages.error(request, strip_tags(error))
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def verify_otp(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        otp_entry = OTPModel.objects.filter(user=user, otp=entered_otp).first()
        
        if otp_entry:
            user.is_active = True  # Activate the user after successful OTP verification
            user.save()
            otp_entry.delete()
            messages.success(request, 'Your account has been verified successfully.')
            return redirect('index')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
    
    if request.GET.get('resend') == 'true':
        # Resend OTP
        otp = generate_otp()
        OTPModel.objects.filter(user=user).delete()  # Clear any previous OTPs
        OTPModel.objects.create(user=user, otp=otp)
        
        send_mail(
            'Your OTP Code',
            f'Your OTP code is {otp}. Please enter this to verify your account.',
            'no-reply@yourdomain.com',
            [user.email],
            fail_silently=False,
        )
        
        messages.info(request, 'A new OTP has been sent to your email.')
    
    return render(request, 'verify_otp.html', {'user_id': user_id})



def logoutPage(request):
    logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('login')
