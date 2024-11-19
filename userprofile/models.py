from django.db import models
from django.contrib.auth.models import User

class StudentInfo(models.Model):
    Edu_levels = [("Undergraduate", "Undergraduate"),
                  ("Graduate", "Graduate"),
                  ("PHD", "PHD")]
    Schools = [("Tandon", "Tandon"),
               ("Stern", "Stern"),
               ("Tisch", "Tisch"),
               ("Gallatin", "Gallatin")]
    semester_choices = [
    ("1st Sem", "1st Sem"),
    ("2nd Sem", "2nd Sem"),
    ("3rd Sem", "3rd Sem"),
    ("4th Sem", "4th Sem"),]
    
    N_id = models.CharField(max_length=9, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    Name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    Education_Level = models.CharField(max_length=50, choices=Edu_levels)
    semester = models.CharField(max_length=20, choices=semester_choices, default="1st Sem")
    Phone_no = models.CharField(max_length=15)  
    School = models.CharField(max_length=50, choices=Schools)
    is_ta = models.BooleanField(default=False)
    ta_course = models.ForeignKey('courseEnroll.CourseInfo', null=True, blank=True, related_name='tas', on_delete=models.SET_NULL)  # Use app label 'coursenroll'
    course_enrolled = models.ManyToManyField('courseEnroll.CourseInfo', related_name='enrolled_students')  # Use app label 'coursenroll'
    advisor = models.ForeignKey('AdminInfo', related_name='advising_students', on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey('userprofile.DepartmentInfo', null=True, blank=True, related_name='students', on_delete=models.SET_NULL,default="CSE")

class AdminInfo(models.Model):
    admin_id = models.CharField(max_length=9)
    Name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField()
    phone_no = models.CharField(max_length=15)

    def __str__(self):
        return self.Name

class DepartmentInfo(models.Model):
    
    department_id = models.CharField(max_length=8, primary_key=True)
    name = models.CharField(default='CSE')

    def __str__(self):
        return self.name 


class FacultyInfo(models.Model):
    faculty_id = models.CharField(max_length=8, primary_key=True)
    Name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    Phone_no = models.CharField(max_length=15)
    ta_students = models.ManyToManyField(StudentInfo, through='TA', related_name='faculty_tas')


    def __str__(self):
        return self.Name 

class TA(models.Model):
    student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
    course = models.ForeignKey('courseEnroll.CourseInfo', on_delete=models.CASCADE)  
    faculty = models.ForeignKey(FacultyInfo, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'course')