from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import StudentInfo

class CustomUserCreationForm(UserCreationForm):
    # Fields from the StudentInfo model
    N_id = forms.CharField(max_length=8, required=True, label="Student ID (N_id)")
    Name = forms.CharField(max_length=100, required=True, label="Name")
    Education_Level = forms.ChoiceField(choices=StudentInfo.Edu_levels, required=True, label="Education Level")
    Phone_no = forms.CharField(max_length=15, required=True, label="Phone Number")
    School = forms.ChoiceField(choices=StudentInfo.Schools, required=True, label="School")

    class Meta:
        model = User  # Use the User model for the basic user information
        fields = ['username', 'email', 'password1', 'password2']  # Fields from the User model

    def save(self, commit=True):
        # Save the user instance
        user = super().save(commit=False)
        if commit:
            user.save()  # Save the User model instance
        
        # Create the StudentInfo instance using the cleaned data
        student_info = StudentInfo.objects.create(
            user=user,  # Link the StudentInfo to the created user
            N_id=self.cleaned_data['N_id'],
            Name=self.cleaned_data['Name'],
            Education_Level=self.cleaned_data['Education_Level'],
            Phone_no=self.cleaned_data['Phone_no'],
            School=self.cleaned_data['School'],
            email=user.email  # Set the email automatically from the User model
        )
        
        return user  # Return the saved user instance