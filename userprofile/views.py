from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.template import loader
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import UserCreationForm ,AuthenticationForm
from .models import *
from courseEnroll.models import *
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from courseEnroll.views import dashboard
from systemadmin.views import admin_dashboard
from django.urls import reverse 


def userinfo(request):
    return HttpResponse("Hello World")

def register_request(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) 
            user.set_password(form.cleaned_data['password1'])  
            user.save() 
            
            student_info = StudentInfo.objects.create(
                user=user,
                N_id=form.cleaned_data['N_id'],
                Name=form.cleaned_data['Name'],
                email=form.cleaned_data['email'],
                Education_Level=form.cleaned_data['Education_Level'],
                Phone_no=form.cleaned_data['Phone_no'],
                School=form.cleaned_data['School']
            )
            login(request, user)  
            return redirect('login')  
    else:
        form = CustomUserCreationForm()
    return render(request, 'userprofile/register.html', {'form': form})


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Check if the user is a superuser
                if user.is_superuser:
                    return redirect('systemadmin:dashboard')  # Redirect to the admin dashboard
                else:
                    return redirect('courseEnroll:dashboard')  # Redirect to the normal dashboard
    else:
        form = AuthenticationForm()
    return render(request, 'userprofile/login.html', {'form': form})

@login_required
def user_profile(request):
    student_info = StudentInfo.objects.get(user=request.user)

    return render(request, 'userprofile/user_profile.html', {'student_info': student_info})

@login_required
def course_enrolled(request):
    student_info = StudentInfo.objects.get(user=request.user)
    courses_enrolled = student_info.course_enrolled.all()

    return render(request, 'courses_enrollement.html', {'courses_enrolled': courses_enrolled})

def logout_request(request):
    logout(request)
    return redirect('userprofile:login') 

def scheduler(request):
    return render(request, "userprofile/scheduler.html")