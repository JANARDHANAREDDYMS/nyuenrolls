from django.test import TestCase
from django.contrib.auth.models import User
from userprofile.models import StudentInfo, AdminInfo, DepartmentInfo, FacultyInfo, TA
from courseEnroll.models import CourseInfo  # Assuming you have a CourseInfo model in courseEnroll app

class ModelsTestCase(TestCase):

    def setUp(self):
        # Create a user instance for StudentInfo
        self.user = User.objects.create_user('john_doe', 'john@example.com', 'johnpassword')

        # Create StudentInfo instance
        self.student = StudentInfo.objects.create(
            N_id="123456789",
            user=self.user,
            Name="John Doe",
            email="john.doe@example.com",
            Education_Level="Undergraduate",
            Phone_no="123-456-7890",
            School="Tandon",
            is_ta=False  # Assuming 'is_ta' is required
        )

        # Create AdminInfo instance
        self.admin = AdminInfo.objects.create(
            admin_id="987654321",
            Name="Admin Name",
            email="admin@example.com",
            phone_no="987-654-3210"
        )

        # Create DepartmentInfo instance
        self.department = DepartmentInfo.objects.create(
            department_id="DEP001",
            name="Computer Science"
        )

        # Create FacultyInfo instance
        self.faculty = FacultyInfo.objects.create(
            faculty_id="FAC123",
            Name="Jane Doe",
            email="jane.doe@example.com",
            Phone_no="321-654-9870"
        )

        # Create CourseInfo instance with all required fields
        self.course = CourseInfo.objects.create(
            course_id="CSE101",
            name="Introduction to Computer Science",
            Department=self.department,
            Instructor=self.faculty,
            course_Capacity=30,
            phd_course_capacity=5,
            class_day='2023-09-01',
            class_time='10:00:00',
            description='An introductory course to computer science.',
            credits=3.0
        )

        # Create TA instance
        self.ta = TA.objects.create(
            student=self.student,
            course=self.course,
            faculty=self.faculty
        )

    def test_student_creation(self):
        self.assertIsInstance(self.student, StudentInfo)
        self.assertEqual(self.student.user.username, 'john_doe')

    def test_admin_creation(self):
        self.assertIsInstance(self.admin, AdminInfo)
        self.assertEqual(self.admin.Name, "Admin Name")

    def test_department_creation(self):
        self.assertIsInstance(self.department, DepartmentInfo)
        self.assertEqual(self.department.name, "Computer Science")

    def test_faculty_creation(self):
        self.assertIsInstance(self.faculty, FacultyInfo)
        self.assertEqual(self.faculty.Name, "Jane Doe")

    def test_ta_creation(self):
        self.assertIsInstance(self.ta, TA)
        self.assertEqual(self.ta.student.Name, "John Doe")
        self.assertEqual(self.ta.course.name, "Introduction to Computer Science")
        self.assertEqual(self.ta.faculty.Name, "Jane Doe")
