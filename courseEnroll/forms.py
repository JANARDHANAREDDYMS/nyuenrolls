from django import forms
from .models import CourseInfo,Enrollment


# Corrected fields list in CourseForm
class CourseForm(forms.ModelForm):
    class Meta:
        model = CourseInfo
        fields = [
            'name', 'Department', 'Instructor', 
            'undergrad_capacity', 'grad_Capacity', 
            'phd_course_capacity', 'class_days', 
            'start_time', 'end_time', 'description', 
            'to_waitlist', 'points_assigned', 'credits'
        ]

    class_days = forms.ChoiceField(
        choices=[
            ('Monday', 'Monday'),
            ('Tuesday', 'Tuesday'),
            ('Wednesday', 'Wednesday'),
            ('Thursday', 'Thursday'),
            ('Friday', 'Friday'),
            ('Saturday', 'Saturday'),
            ('Sunday', 'Sunday'),
        ],
        widget=forms.RadioSelect,  # Use RadioSelect to display it as a set of radio buttons
        required=False,  # Optional field; you can set this to True if you want it to be required
    )
    
    start_time = forms.TimeField(widget=forms.TimeInput(format='%H:%M'), required=False)
    end_time = forms.TimeField(widget=forms.TimeInput(format='%H:%M'), required=False)

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'course', 'points_assigned', 'is_waitlisted']
