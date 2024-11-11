from django.urls import path
from . import views

app_name = 'courseEnroll'

urlpatterns = [
    path("dashboard/",views.dashboard,name="dashboard"), 
    path('search_courses/', views.search_courses, name='search_courses'),
    path('select_courses',views.select_courses,name='select_courses'), 
    path('delete_selected_courses/', views.delete_selected_courses, name='delete_selected_courses'),
    path('update_enrollment/', views.update_enrollment, name='update_enrollment'),
]
