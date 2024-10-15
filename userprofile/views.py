from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.template import loader
from .forms import UserInfoForm, create_user_form
from django.contrib.auth.forms import UserCreationForm 
from django.contrib import messages

def userinfo(request):
    return HttpResponse("Hello World")

def user_info_view(request):
    if request.method == 'POST':
        form = UserInfoForm(request.POST)
        if form.is_valid():
            form.save()  # Save the data to the database
            form = UserInfoForm
               
    else:
        form = UserInfoForm()

    return render(request, 'user_info_form.html', {'form': form})

def login_request(request):
    context = {}
    return render(request,'login.html',context)

def register_request(request): 
    form = create_user_form()

    if request.method =="POST":
        form =  create_user_form(request.POST)
        if form.is_valid():
            form.save()
            user_name = form.cleaned_data.get('username')
            messages.success(request, 'Account for' +user_name+ 'created' )
            return redirect('login')
    else:
        form = UserInfoForm()

    context ={'form': form}
    return render(request,'register.html',context)

def dashboard(request):
    return render(request, "userprofile/dashboard.html")

def scheduler(request):
    return render(request, "userprofile/scheduler.html")