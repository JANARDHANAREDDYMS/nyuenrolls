from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test

def admin_required(user):
    return user.is_superuser

# Create your views here.
@login_required
@user_passes_test(admin_required)
def admin_dashboard(request):
    return render(request, 'systemadmin/admin_dashboard.html')

def logout_request(request):
    logout(request)
    return redirect('userprofile:login') 