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
    section =  models.CharField(default='A',max_length=1)
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
    
    def to_dict(self):
        return {
            'course_code': self.course_code,
            'department': self.department,
            # Include other fields you need
        }
    
    waitlist_capacity = models.IntegerField(default=35)

class Enrollment(models.Model):
    student = models.ForeignKey('userprofile.StudentInfo', on_delete=models.CASCADE, related_name='enrollments')  # Use app label 'userprofile'
    course = models.ForeignKey(CourseInfo, on_delete=models.CASCADE, related_name='enrollments')
    points_assigned = models.DecimalField(decimal_places=1, max_digits=3, null=True, blank=True)
    is_waitlisted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')
    
    def __str__(self):
        return f'{self.student.Name} enrolled in {self.course.name}'
    
class OverrideForm(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ]

    form_id = models.AutoField(primary_key=True)
    date = models.DateField(default=timezone.now)
    course_code = models.ForeignKey('courseEnroll.CourseInfo', on_delete=models.CASCADE, related_name='override_forms')
    department = models.ForeignKey('userprofile.DepartmentInfo', on_delete=models.SET_NULL, null=True, related_name='override_forms')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    student = models.ForeignKey('userprofile.StudentInfo', on_delete=models.CASCADE, related_name='override_forms')
    explanation = models.TextField()

    def __str__(self):
        return f"Override Form {self.form_id} - {self.course_code.name} - {self.status}"

    @property
    def student_name(self):
        return self.student.Name
    
    @property
    def student_id(self):
        return self.student.N_id