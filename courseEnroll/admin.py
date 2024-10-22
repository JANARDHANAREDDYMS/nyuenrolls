from django.contrib import admin
from .models import CourseInfo, Enrollment

@admin.register(CourseInfo)
class CourseInfoAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'name', 'Department', 'Instructor', 'credits')  # Fields to display in the list view
    search_fields = ('course_id', 'name', 'Instructor__name')  # Fields to search on
    list_filter = ('Department', 'Instructor')  # Filters to apply on the right side

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'points_assigned', 'is_waitlisted')  # Fields to display in the list view
    search_fields = ('student__name', 'course__name')  # Fields to search on
    list_filter = ('is_waitlisted', 'course')  # Filters to apply on the right side
    raw_id_fields = ('student', 'course')  # To use a more efficient lookup for foreign keys
