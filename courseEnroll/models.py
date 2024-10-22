from django.db import models
# Create your models here.

class CourseInfo(models.Model):
    course_id = models.CharField(max_length=11, primary_key=True)
    name = models.CharField(max_length=100)
    Department = models.ForeignKey('userprofile.DepartmentInfo',related_name='courses',on_delete=models.SET_NULL,null=True)
    Instructor = models.OneToOneField('userprofile.FacultyInfo', on_delete=models.SET_NULL, related_name='course',null=True)
    course_Capacity = models.IntegerField()
    phd_course_capacity = models.IntegerField()
    class_day = models.DateField()
    class_time = models.TimeField()
    description = models.CharField(max_length=1000)
    points_assigned =  models.CharField(max_length=3,null=True)
    credits = models.DecimalField(decimal_places=1, max_digits=3)

class Enrollment(models.Model):
    student = models.ForeignKey('userprofile.StudentInfo', on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(CourseInfo, on_delete=models.CASCADE, related_name='enrollments')
    points_assigned = models.DecimalField(decimal_places=1, max_digits=3, null=True, blank=True)  
    is_waitlisted = models.BooleanField(default=False)  

    class Meta:
        unique_together = ('student', 'course')  