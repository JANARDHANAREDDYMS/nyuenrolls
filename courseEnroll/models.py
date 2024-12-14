from django.db import models

from django.utils import timezone

from django.db import models

class CourseInfo(models.Model):
    # Choices for class days
    CLASS_DAYS = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]

    # Choices for schools
    SCHOOLS = [
        ("Tandon", "Tandon"),
        ("Stern", "Stern"),
        ("Tisch", "Tisch"),
        ("Gallatin", "Gallatin"),
    ]

    # Fields
    course_id = models.CharField(max_length=11, primary_key=True)
    name = models.CharField(max_length=100)
    school = models.CharField(max_length=20, choices=SCHOOLS, default="Tandon")
    Department = models.ForeignKey(
        'userprofile.DepartmentInfo',
        related_name='courses',
        on_delete=models.SET_NULL,
        null=True
    )
    Instructor = models.ForeignKey(
        'userprofile.FacultyInfo',
        on_delete=models.SET_NULL,
        related_name='courses',
        null=True
    )
    undergrad_capacity = models.IntegerField(blank=True, default=0)
    grad_Capacity = models.IntegerField(default=0)  # Corrected field name
    phd_course_capacity = models.IntegerField(default=0)
    section = models.CharField(default='A', max_length=1)
    class_days = models.CharField(
        max_length=9,
        blank=True,
        null=True,
        choices=CLASS_DAYS
    )
    start_time = models.TimeField(default='09:00:00', blank=True)
    end_time = models.TimeField(default='09:00:00', blank=True)
    description = models.TextField(max_length=1000)  # Changed to `TextField` for better long descriptions
    to_waitlist = models.BooleanField(default=False)
    points_assigned = models.IntegerField(null=True, blank=True)
    credits = models.DecimalField(decimal_places=1, max_digits=3, default=0.0)
    waitlist_capacity = models.IntegerField(default=35)

    # Methods
    def __str__(self):
        return f"{self.name} ({self.course_id})"

    def to_dict(self):
        return {
            'course_id': self.course_id,
            'name': self.name,
            'school': self.school,
            'Department': self.Department.name if self.Department else None,
            'Instructor': self.Instructor.name if self.Instructor else None,
            'undergrad_capacity': self.undergrad_capacity,
            'grad_Capacity': self.grad_Capacity,
            'phd_course_capacity': self.phd_course_capacity,
            'section': self.section,
            'class_days': self.class_days,
            'start_time': str(self.start_time),
            'end_time': str(self.end_time),
            'description': self.description,
            'to_waitlist': self.to_waitlist,
            'points_assigned': self.points_assigned,
            'credits': float(self.credits),
            'waitlist_capacity': self.waitlist_capacity,
        }
    
    waitlist_capacity = models.IntegerField(default=35)

class Enrollment(models.Model):
    student = models.ForeignKey('userprofile.StudentInfo', on_delete=models.CASCADE, related_name='enrollments')  # Use app label 'userprofile'
    course = models.ForeignKey(CourseInfo, on_delete=models.CASCADE, related_name='enrollments')
    points_assigned = models.DecimalField(decimal_places=1, max_digits=3, null=True, blank=True)
    true_points = models.DecimalField(decimal_places=1,max_digits=3,null=True,blank=True)
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
    

class PreRegInfo(models.Model):
    student_id = models.OneToOneField(
            'userprofile.StudentInfo', 
            on_delete=models.CASCADE, 
            primary_key=True  
        )
    course1 = models.ForeignKey(
            CourseInfo, 
            on_delete=models.CASCADE, 
            related_name='primary_course', 
            null=True, 
            blank=True
        )
    course2 = models.ForeignKey(
            CourseInfo, 
            on_delete=models.CASCADE, 
            related_name='secondary_course', 
            null=True, 
            blank=True
        )
    course3 = models.ForeignKey(
            CourseInfo, 
            on_delete=models.CASCADE, 
            related_name='tertiary_course', 
            null=True, 
            blank=True
        )

    def __str__(self):
            return f"Pre-Registration Info for {self.N_id.name}"