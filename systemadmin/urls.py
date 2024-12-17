

from django.urls import path
from .views import admin_dashboard,course_add,course_update,delete_course, prereg, override, modify_override,get_course_details, search_course_enrollment, search_student_enrollment, remove_student_course, remove_student_fromcourse

app_name = 'systemadmin'

urlpatterns = [
    path('admin_dashboard/', admin_dashboard, name='dashboard'),
    path('course/add/', course_add, name='course_add'),
    path('course/update/', course_update, name='course_update'),
    path('prereg/', prereg, name='prereg' ),
    path('override/', override, name='override' ),
    path('override/update', modify_override, name='modify_override' ),
    path('course_details/<str:course_id>/', get_course_details, name='get_course_details'),
    path('delete_course/<str:course_id>/', delete_course, name='delete_course'),
    path('course/enrollment/', search_course_enrollment, name='search_course_enrollment'),
    path('student/enrollment/', search_student_enrollment, name='search_student_enrollment'),
    path('remove_student_course/', remove_student_course, name='remove_student_course'),
    path('remove_student_fromcourse/', remove_student_fromcourse, name='remove_student_fromcourse'),
]