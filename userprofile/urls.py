from django.urls import path
from . import views

urlpatterns = [
    path("",views.userinfo,name="userinfo"),
    path('user_info/', views.user_info_view, name='user_info_form'),
    path('login/',views.login_request,name='login'),
    path('register/',views.register_request,name='register'),
    path("course_dashboard/",views.dashboard,name="dashboard"),
    path("scheduler/", views.scheduler, name="scheduler")
]

