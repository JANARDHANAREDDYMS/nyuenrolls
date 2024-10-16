from django.urls import path
from . import views

urlpatterns = [
    path("",views.userinfo,name="userinfo"),
    path('login/',views.login_request,name='login'),
    path('register/',views.register_request,name='register'),
    path("course_dashboard/",views.dashboard,name="dashboard"),
    path("scheduler/", views.scheduler, name="scheduler"),
    path('logout/', views.logout_request, name='logout'),
]

