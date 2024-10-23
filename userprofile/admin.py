from django.contrib import admin
from .models import StudentInfo, FacultyInfo, TA, DepartmentInfo,AdminInfo

@admin.register(StudentInfo)
class StudentInfoAdmin(admin.ModelAdmin):
    list_display = ['N_id', 'Name', 'email', 'Education_Level', 'Phone_no', 'School']


@admin.register(FacultyInfo)
class FacultyInfoAdmin(admin.ModelAdmin):
    list_display = ['faculty_id', 'Name', 'email', 'Phone_no']

@admin.register(TA)
class TAAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'faculty']

@admin.register(DepartmentInfo)
class DepartmentInfoAdmin(admin.ModelAdmin):
    list_display= ['department_id','name']

@admin.register(AdminInfo)
class AdminInfoAdmin(admin.ModelAdmin):
    list_display = ['admin_id','Name','email','phone_no']