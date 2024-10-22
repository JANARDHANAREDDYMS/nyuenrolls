from django.contrib import admin
from .models import StudentInfo, FacultyInfo, TA

@admin.register(StudentInfo)
class StudentInfoAdmin(admin.ModelAdmin):
    list_display = ['N_id', 'Name', 'email', 'Education_Level', 'Phone_no', 'School']


@admin.register(FacultyInfo)
class FacultyInfoAdmin(admin.ModelAdmin):
    list_display = ['faculty_id', 'Name', 'email', 'Phone_no']

@admin.register(TA)
class TAAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'faculty']