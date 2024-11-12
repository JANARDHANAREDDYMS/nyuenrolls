from django.contrib import admin
from .models import CourseInfo, Enrollment
from .forms import EnrollmentForm

@admin.register(CourseInfo)
class CourseInfoAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'name', 'Department', 'Instructor', 'credits','undergrad_capacity', 'grad_Capacity', 'phd_course_capacity', 'class_days', 'start_time', 'end_time', 'to_waitlist')
    search_fields = ('course_id', 'name', 'Instructor__name')
    list_filter = ('Department', 'Instructor', 'to_waitlist')
    ordering = ('name',)
    def enrollment_count(self, obj):
        return obj.enrollments.count()
    enrollment_count.short_description = 'Current Enrollments'
    
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'points_assigned', 'is_waitlisted', 'created_at')
    search_fields = ('student__name', 'course__name')
    list_filter = ('is_waitlisted', 'course', 'created_at')
    raw_id_fields = ('student', 'course')
    ordering = ('course', 'student', 'created_at')
    actions = ['mark_waitlisted', 'remove_from_waitlist']

    # Custom actions to manage waitlisting
    def mark_waitlisted(self, request, queryset):
        queryset.update(is_waitlisted=True)
        self.message_user(request, "Selected enrollments marked as waitlisted.")

    def remove_from_waitlist(self, request, queryset):
        queryset.update(is_waitlisted=False)
        self.message_user(request, "Selected enrollments removed from waitlist.")
    
    mark_waitlisted.short_description = "Mark selected enrollments as waitlisted"
    remove_from_waitlist.short_description = "Remove selected enrollments from waitlist"

