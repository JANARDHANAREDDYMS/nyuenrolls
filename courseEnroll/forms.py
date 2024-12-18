from django import forms
from .models import CourseInfo,OverrideForm,PreRegInfo
from userprofile.models import StudentInfo,DepartmentInfo
from django.utils import timezone


from django import forms
from .models import CourseInfo, OverrideForm
from userprofile.models import StudentInfo, DepartmentInfo

class OverrideFormSubmission(forms.ModelForm):
    course_code = forms.ModelChoiceField(
        queryset=CourseInfo.objects.none(),  # Initially empty
        empty_label="Select a Course",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = OverrideForm
        fields = ['course_code', 'explanation']
        widgets = {
            'explanation': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Provide a detailed explanation...'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract the user from kwargs
        super().__init__(*args, **kwargs)
        
        if user:
            try:
                student = StudentInfo.objects.get(user=user)
                
                courses_outside_department = CourseInfo.objects.exclude(Department=student.department)
            
            # Get specific courses
                specific_courses = CourseInfo.objects.filter(
                    course_id__in=["CSGY6033D", "CSGY6033", "CSGY6033B", "CSGY6033C"]
                )
                
                # Combine the querysets
                courses_for_override = courses_outside_department | specific_courses
                
                self.fields['course_code'].queryset = courses_for_override

                
                # Store the student for the save method
                self.student = student
            except StudentInfo.DoesNotExist:
                self.student = None
                self.fields['course_code'].queryset = CourseInfo.objects.none()

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.student = self.student
        instance.department = instance.course_code.Department
        if commit:
            instance.save()
        return instance

from django import forms
from .models import CourseInfo

class CourseForm(forms.ModelForm):
    class Meta:
        model = CourseInfo
        fields = [
            'name', 
            'Department',  # Updated from 'Department'
            'Instructor',  # Updated from 'Instructor'
            'grad_Capacity',  # Updated from 'grad_Capacity'
            'phd_course_capacity', 
            'class_days', 
            'start_time', 
            'end_time', 
            'description', 
            'to_waitlist', 
            'points_assigned', 
            'credits',
            'waitlist_capacity',  # Added to include in the form
        ]

    # Updated class_days to align with the new model
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

    # Added default time input widgets for better user experience
    start_time = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M', attrs={'placeholder': 'HH:MM'}),
        required=False,
        help_text="Format: HH:MM (24-hour format)",
    )

    end_time = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M', attrs={'placeholder': 'HH:MM'}),
        required=False,
        help_text="Format: HH:MM (24-hour format)",
    )




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