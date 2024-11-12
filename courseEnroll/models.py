from django.db import models
from django.utils import timezone

class CourseInfo(models.Model):
    class_days = [
            ('Monday', 'Monday'),
            ('Tuesday', 'Tuesday'),
            ('Wednesday', 'Wednesday'),
            ('Thursday', 'Thursday'),
            ('Friday', 'Friday'),
            ('Saturday', 'Saturday'),
            ('Sunday', 'Sunday'),
        ]
    Schools = [("Tandon", "Tandon"),
               ("Stern", "Stern"),
               ("Tisch", "Tisch"),
               ("Gallatin", "Gallatin")]
    course_id = models.CharField(max_length=11, primary_key=True)
    name = models.CharField(max_length=100)
    school =  models.CharField(choices=Schools,default="Tandon")
    Department = models.ForeignKey('userprofile.DepartmentInfo', related_name='courses', on_delete=models.SET_NULL, null=True)
    Instructor = models.OneToOneField('userprofile.FacultyInfo', on_delete=models.SET_NULL, related_name='course', null=True)
    undergrad_capacity = models.IntegerField(blank=True)
    grad_Capacity = models.IntegerField()
    phd_course_capacity = models.IntegerField()
    class_days = models.CharField(max_length=100, blank=True, null=True, choices=class_days)  
    start_time = models.TimeField(default='09:00:00', blank=True)
    end_time = models.TimeField(default='09:00:00', blank=True)
    description = models.CharField(max_length=1000)
    to_waitlist = models.BooleanField(blank=True, default=False)
    points_assigned = models.IntegerField( null=True, blank=True)
    credits = models.DecimalField(decimal_places=1, max_digits=3)
    
    def __str__(self):
        return self.name
    
    waitlist_capacity = models.IntegerField(default=35)

class Enrollment(models.Model):
    student = models.ForeignKey('userprofile.StudentInfo', on_delete=models.CASCADE, related_name='enrollments')  # Use app label 'userprofile'
    course = models.ForeignKey(CourseInfo, on_delete=models.CASCADE, related_name='enrollments')
    points_assigned = models.DecimalField(decimal_places=1, max_digits=3, null=True, blank=True)
    is_waitlisted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.is_waitlisted and self.course.enrollments.count() >= self.course.undergrad_capacity + self.course.grad_Capacity + self.course.phd_course_capacity:
            self.is_waitlisted = True
        super().save(*args, **kwargs)
    class Meta:
        unique_together = ('student', 'course')
    
    def __str__(self):
        return f'{self.student.Name} enrolled in {self.course.name}'