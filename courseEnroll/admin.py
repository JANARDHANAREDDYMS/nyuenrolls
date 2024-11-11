from django.contrib import admin
from .models import CourseInfo, Enrollment

@admin.register(CourseInfo)
class CourseInfoAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'name', 'Department', 'Instructor', 'credits','undergrad_capacity', 'grad_Capacity', 'phd_course_capacity', 'class_days', 'start_time', 'end_time', 'to_waitlist')
    search_fields = ('course_id', 'name', 'Instructor__name')
    list_filter = ('Department', 'Instructor', 'to_waitlist')
    ordering = ('name',)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'points_assigned', 'is_waitlisted','created_at')
    search_fields = ('student__name', 'course__name')
    list_filter = ('is_waitlisted', 'course','created_at')
    raw_id_fields = ('student', 'course')
    ordering = ('course', 'student','created_at')
