from django.urls import path
from . import views

app_name = 'courseEnroll'

urlpatterns = [
    path("dashboard/",views.dashboard,name="dashboard"), 
    path('search_courses/', views.search_courses, name='search_courses'),
    path('select_courses',views.select_courses,name='select_courses'), 
    path('delete_selected_courses/', views.delete_selected_courses, name='delete_selected_courses'),
    path('update_enrollment/', views.update_enrollment, name='update_enrollment'),
    path('course/<str:course_id>/', views.course_enrollment, name='course_enrollment'),
    path('submit_override/', views.submit_override, name='submit_override'),
path('course/delete/<int:course_id>/', views.delete_selected_courses, name='delete_course'),
path('swap-courses/', views.swap_courses, name='swap_courses'),

]
