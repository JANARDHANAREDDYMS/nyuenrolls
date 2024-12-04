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
from collections import defaultdict


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
            return redirect('userprofile:login')  
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
    departments = defaultdict(list)  # To store departments with their respective courses
    dept_objs = DepartmentInfo.objects.all()

    for department in dept_objs:
        # Get courses for the department
        courses = CourseInfo.objects.filter(Department=department)
        
        # Dictionary to organize courses by their base course ID
        course_dict = defaultdict(lambda: {"name": "", "day": [], "start": [], "end": [], "start_mins": [], "end_mins": [], "sections": []})
        
        for course in courses:
            # Remove the last character if it's a letter
            if course.course_id[-1].isalpha():
                base_course_id = course.course_id[:-1]
                section = course.course_id[-1]  # The removed letter becomes the section
            else:
                base_course_id = course.course_id
                section = "A"  # No section if the last character isn't a letter

            if base_course_id not in course_dict:
                # Add course metadata for first occurrence
                course_dict[base_course_id].update({
                    "name": f"{base_course_id}: {course.name}"
                })
            
            # Append the section if available
            if section and section not in course_dict[base_course_id]["sections"]:
                course_dict[base_course_id]["sections"].append(section)
                course_dict[base_course_id]["start"].append(course.start_time.hour)
                course_dict[base_course_id]["start_mins"].append(f"{course.start_time.minute:02}")
                course_dict[base_course_id]["end"].append(course.end_time.hour)
                course_dict[base_course_id]["end_mins"].append(f"{course.end_time.minute:02}")  # Formatted to two digits
                course_dict[base_course_id]["day"].append(course.class_days)
        
        # Add to the department's course list
        departments[department.name].extend(course_dict.values())

    return render(request, "userprofile/scheduler.html", {"depts": dict(departments)})
