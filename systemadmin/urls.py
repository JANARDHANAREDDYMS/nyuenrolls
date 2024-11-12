from django.urls import path
from .views import admin_dashboard,course_add,course_update,course_delete, prereg, override

app_name = 'systemadmin'

urlpatterns = [
    path('admin_dashboard/', admin_dashboard, name='dashboard'),
    path('course/add/', course_add, name='course_add'),
    path('course/update/', course_update, name='course_update'),
    path('course/delete/', course_delete, name='course_delete'),
    path('prereg/', prereg, name='prereg' ),
    path('override/', override, name='override' )
]