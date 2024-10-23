from django.urls import path
from . import views

app_name = 'userprofile'

urlpatterns = [
    path("",views.userinfo,name="userinfo"),
    path('login/',views.login_request,name='login'),
    path('register/',views.register_request,name='register'),
    path('user_profile/',views.user_profile,name="user_profile"),
    path("scheduler/", views.scheduler, name="scheduler"),
    path('logout/', views.logout_request, name='logout'),
]

