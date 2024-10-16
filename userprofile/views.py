from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.template import loader
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import UserCreationForm ,AuthenticationForm
from .models import StudentInfo
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def userinfo(request):
    return HttpResponse("Hello World")

# def user_info_view(request):
#     if request.method == 'POST':
#         form = UserInfoForm(request.POST)
#         if form.is_valid():
#             form.save()  # Save the data to the database
#             form = UserInfoForm
               
#     else:
#         form = UserInfoForm()

#     return render(request, 'userprofile/user_info_form.html', {'form': form})


def register_request(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Create the user without saving yet
            user.set_password(form.cleaned_data['password'])  # Set the password
            user.save()  # Now save the user
            
            # Create StudentInfo instance
            student_info = StudentInfo.objects.create(
                user=user,
                N_id=form.cleaned_data['N_id'],
                Name=form.cleaned_data['Name'],
                email=form.cleaned_data['email'],
                Education_Level=form.cleaned_data['Education_Level'],
                Phone_no=form.cleaned_data['Phone_no'],
                School=form.cleaned_data['School']
            )
            login(request, user)  # Log the user in
            return redirect('dashboard')  # Redirect to the dashboard or any other page
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
                return redirect('dashboard')  # Redirect to the dashboard after successful login
    else:
        form = AuthenticationForm()
    return render(request, 'userprofile/login.html', {'form': form})


@login_required
def dashboard(request):
    student_info = StudentInfo.objects.get(user=request.user)
    return render(request, 'userprofile/dashboard.html', {'student_info': student_info})

def logout_request(request):
    logout(request)
    return redirect('login') 

def scheduler(request):
    return render(request, "userprofile/scheduler.html")