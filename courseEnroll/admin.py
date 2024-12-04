from django.contrib import admin
from .models import CourseInfo, Enrollment

@admin.register(CourseInfo)
class CourseInfoAdmin(admin.ModelAdmin):
    list_display = (
        'course_id', 
        'name', 
        'Department',  # Updated field name
        'Instructor',  # Updated field name
        'credits', 
        'undergrad_capacity', 
        'grad_Capacity',  # Updated field name
        'phd_course_capacity', 
        'class_days', 
        'start_time', 
        'end_time', 
        'to_waitlist'
    )
    search_fields = ('course_id', 'name', 'instructor__name')  # Updated field name
    list_filter = ('Department', 'Instructor', 'to_waitlist')  # Updated field names
    ordering = ('name',)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'points_assigned', 'is_waitlisted','created_at')
    search_fields = ('student__name', 'course__name')
    list_filter = ('is_waitlisted', 'course','created_at')
    raw_id_fields = ('student', 'course')
    ordering = ('course', 'student','created_at')
