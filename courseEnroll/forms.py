from django import forms
from .models import CourseInfo,OverrideForm,PreRegInfo
from userprofile.models import StudentInfo,DepartmentInfo
from django.utils import timezone


class OverrideFormSubmission(forms.ModelForm):
    class Meta:
        model = OverrideForm
        fields = ['course_code', 'explanation']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract the user from kwargs
        super().__init__(*args, **kwargs)

        if user:
            try:
                student = StudentInfo.objects.get(user=user)
                student_department = student.department
                # Exclude courses from the student's department
                self.fields['course_code'].queryset = CourseInfo.objects.exclude(Department=student_department)
            except StudentInfo.DoesNotExist:
                self.fields['course_code'].queryset = CourseInfo.objects.none()  # No courses available
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Automatically set the department of the selected course
        if instance.course_code:
            instance.department = instance.course_code.Department
        if commit:
            instance.save()
        return instance

class CourseForm(forms.ModelForm):
    class Meta:
        model = CourseInfo
        fields = ['name', 'Department', 'Instructor', 'grad_Capacity', 'phd_course_capacity', 'class_days', 
                  'start_time', 'end_time', 'description', 'to_waitlist', 'points_assigned', 'credits']

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
        widget=forms.RadioSelect, 
        required=False, 
    )
    
    start_time = forms.TimeField(widget=forms.TimeInput(format='%H:%M'), required=False)
    end_time = forms.TimeField(widget=forms.TimeInput(format='%H:%M'), required=False)



class PreRegInfoForm(forms.ModelForm):
    class Meta:
        model = PreRegInfo
        fields = ['course1', 'course2', 'course3']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract the user from kwargs
        super().__init__(*args, **kwargs)

        if user:
            try:
                student = StudentInfo.objects.get(user=user)
                # Filter courses available for the student
                self.fields['course1'].queryset = CourseInfo.objects.all()
                self.fields['course2'].queryset = CourseInfo.objects.all()
                self.fields['course3'].queryset = CourseInfo.objects.all()
            except StudentInfo.DoesNotExist:
                # If no StudentInfo found, set empty queryset
                self.fields['course1'].queryset = CourseInfo.objects.none()
                self.fields['course2'].queryset = CourseInfo.objects.none()
                self.fields['course3'].queryset = CourseInfo.objects.none()