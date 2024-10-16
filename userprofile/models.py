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
    
    N_id = models.CharField(max_length=8, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    Name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    Education_Level = models.CharField(max_length=50, choices=Edu_levels)
    Phone_no = models.CharField(max_length=15)  
    School = models.CharField(max_length=50, choices=Schools)
    ta_course = models.ForeignKey('CourseInfo', null=True, blank=True, related_name='tas', on_delete=models.SET_NULL)
    is_ta = models.BooleanField(default=False)
    # course_enrolled = models.ManyToManyField('CourseInfo', related_name='enrolled_students')

class CourseInfo(models.Model):
    course_id = models.CharField(max_length=11, primary_key=True)
    name = models.CharField(max_length=100)
    Instructor = models.OneToOneField('FacultyInfo', on_delete=models.SET_NULL, related_name='course', null=True)
    course_Capacity = models.IntegerField()
    phd_course_capacity = models.IntegerField()
    class_day = models.DateField()
    class_time = models.TimeField()
    description = models.CharField(max_length=1000)
    credits = models.DecimalField(decimal_places=1, max_digits=3)

class FacultyInfo(models.Model):
    faculty_id = models.CharField(max_length=8, primary_key=True)
    Name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    Phone_no = models.CharField(max_length=15) 
    ta_students = models.ManyToManyField(StudentInfo, through='TA', related_name='faculty_tas')

class TA(models.Model):
    student = models.OneToOneField(StudentInfo, on_delete=models.CASCADE)
    course = models.ForeignKey(CourseInfo, on_delete=models.CASCADE)
    faculty = models.ForeignKey(FacultyInfo, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'course')  