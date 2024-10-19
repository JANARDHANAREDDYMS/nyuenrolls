from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import StudentInfo

class CustomUserCreationForm(UserCreationForm):
    N_id = forms.CharField(max_length=8, required=True, label="Student ID (N_id)")
    Name = forms.CharField(max_length=100, required=True, label="Name")
    Education_Level = forms.ChoiceField(choices=StudentInfo.Edu_levels, required=True, label="Education Level")
    Phone_no = forms.CharField(max_length=15, required=True, label="Phone Number")
    School = forms.ChoiceField(choices=StudentInfo.Schools, required=True, label="School")

    class Meta:
        model = User  
        fields = ['username', 'email', 'password1', 'password2']  

    def save(self, commit=True):
        # Save the user first
        user = super().save(commit=commit)
        
        # Ensure that the user is saved before creating the StudentInfo
        if commit:
            student_info = StudentInfo.objects.create(
                user=user,  # Now we reference the saved user
                N_id=self.cleaned_data['N_id'],
                Name=self.cleaned_data['Name'],
                Education_Level=self.cleaned_data['Education_Level'],
                Phone_no=self.cleaned_data['Phone_no'],
                School=self.cleaned_data['School'],
                email=user.email  # Assuming email is a field in StudentInfo
            )
        
        return user 