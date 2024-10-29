from django.urls import path
from .views import admin_dashboard,course_add

app_name = 'systemadmin'

urlpatterns = [
    path('dashboard/', admin_dashboard, name='dashboard'),
    path('course/add/', course_add, name='course_add'),
]