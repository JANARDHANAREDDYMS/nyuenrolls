# tests.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import CourseInfo, Enrollment
from userprofile.models import DepartmentInfo, FacultyInfo, StudentInfo  # Assuming these models exist

class CourseInfoModelTest(TestCase):
    def setUp(self):
        # Create related models for ForeignKey and OneToOneField dependencies
        self.department = DepartmentInfo.objects.create(name="Computer Science")
        self.instructor = FacultyInfo.objects.create(name="Dr. Smith")

    def test_course_creation(self):
        course = CourseInfo.objects.create(
            course_id="CS101",
            name="Intro to Computer Science",
            Department=self.department,
            Instructor=self.instructor,
            course_Capacity=30,
            phd_course_capacity=5,
            class_day="2024-09-01",
            class_time="10:00:00",
            description="An introductory course in computer science.",
            to_waitlist=True,
            points_assigned="3",
            credits=3.0
        )
        self.assertEqual(course.name, "Intro to Computer Science")
        self.assertEqual(course.course_Capacity, 30)
        self.assertTrue(course.to_waitlist)

    def test_course_capacity_validation(self):
        course = CourseInfo(
            course_id="CS102",
            name="Data Structures",
            Department=self.department,
            Instructor=self.instructor,
            course_Capacity=-10,  # Invalid capacity
            phd_course_capacity=5,
            class_day="2024-09-01",
            class_time="12:00:00",
            description="Advanced data structures.",
            credits=3.0
        )
        with self.assertRaises(ValidationError):
            course.full_clean()  # Should raise ValidationError for invalid capacity

class EnrollmentModelTest(TestCase):
    def setUp(self):
        # Set up course and student instances for testing
        self.department = DepartmentInfo.objects.create(name="Computer Science")
        self.instructor = FacultyInfo.objects.create(name="Dr. Jones")
        self.course = CourseInfo.objects.create(
            course_id="CS103",
            name="Algorithms",
            Department=self.department,
            Instructor=self.instructor,
            course_Capacity=30,
            phd_course_capacity=5,
            class_day="2024-09-01",
            class_time="14:00:00",
            description="An advanced algorithms course.",
            credits=3.0
        )
        self.student = StudentInfo.objects.create(name="John Doe")

    def test_enrollment_creation(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            points_assigned=2.0,
            is_waitlisted=True
        )
        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.course, self.course)
        self.assertTrue(enrollment.is_waitlisted)

    def test_unique_enrollment(self):
        # Create an initial enrollment
        Enrollment.objects.create(student=self.student, course=self.course)
        # Attempt to create a duplicate enrollment
        duplicate_enrollment = Enrollment(student=self.student, course=self.course)
        with self.assertRaises(ValidationError):
            duplicate_enrollment.full_clean()  # Should raise ValidationError due to unique_together constraint
