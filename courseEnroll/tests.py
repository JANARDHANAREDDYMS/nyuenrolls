from django.test import TestCase
from django.contrib.auth.models import User
from .models import CourseInfo, Enrollment
from userprofile.models import DepartmentInfo, FacultyInfo, StudentInfo

class CourseInfoModelTest(TestCase):

    def setUp(self):
        # Create related DepartmentInfo and FacultyInfo instances
        self.department = DepartmentInfo.objects.create(
            department_id='CSE',
            name='Computer Science'
        )
        self.faculty = FacultyInfo.objects.create(
            faculty_id='FAC123',
            Name='Dr. Smith',
            email='dr.smith@example.com',
            Phone_no='123-456-7890'
        )

        # Create CourseInfo instance
        self.course = CourseInfo.objects.create(
            course_id='CSE101',
            name='Introduction to Computer Science',
            Department=self.department,
            Instructor=self.faculty,
            course_Capacity=30,
            phd_course_capacity=5,
            class_day='2023-01-15',
            class_time='10:00:00',
            description='An introductory course to Computer Science.',
            to_waitlist=False,
            points_assigned='100',
            credits=3.0
        )

    def test_course_creation(self):
        self.assertIsInstance(self.course, CourseInfo)
        self.assertEqual(self.course.name, 'Introduction to Computer Science')
        self.assertEqual(self.course.Department, self.department)
        self.assertEqual(self.course.Instructor, self.faculty)
        self.assertEqual(self.course.course_Capacity, 30)
        self.assertEqual(self.course.phd_course_capacity, 5)
        self.assertEqual(str(self.course.class_day), '2023-01-15')
        self.assertEqual(str(self.course.class_time), '10:00:00')
        self.assertEqual(self.course.description, 'An introductory course to Computer Science.')
        self.assertFalse(self.course.to_waitlist)
        self.assertEqual(self.course.points_assigned, '100')
        self.assertEqual(self.course.credits, 3.0)

    def test_course_string_representation(self):
        self.assertEqual(str(self.course), self.course.name)

class EnrollmentModelTest(TestCase):

    def setUp(self):
        # Create User instance for StudentInfo
        self.user = User.objects.create_user(
            username='johndoe',
            email='john.doe@example.com',
            password='password123'
        )

        # Create StudentInfo instance
        self.student = StudentInfo.objects.create(
            N_id='N12345678',
            user=self.user,
            Name='John Doe',
            email='john.doe@example.com',
            Education_Level='Undergraduate',
            Phone_no='555-555-5555',
            School='Tandon',
            is_ta=False
        )

        # Create DepartmentInfo and FacultyInfo instances
        self.department = DepartmentInfo.objects.create(
            department_id='CSE',
            name='Computer Science'
        )
        self.faculty = FacultyInfo.objects.create(
            faculty_id='FAC456',
            Name='Dr. Johnson',
            email='dr.johnson@example.com',
            Phone_no='098-765-4321'
        )

        # Create CourseInfo instance
        self.course = CourseInfo.objects.create(
            course_id='CSE102',
            name='Data Structures',
            Department=self.department,
            Instructor=self.faculty,
            course_Capacity=25,
            phd_course_capacity=3,
            class_day='2023-02-01',
            class_time='14:00:00',
            description='An intermediate course on data structures.',
            to_waitlist=True,
            points_assigned='50',
            credits=3.0
        )

        # Create Enrollment instance
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            points_assigned=3.0,
            is_waitlisted=False
        )

    def test_enrollment_creation(self):
        self.assertIsInstance(self.enrollment, Enrollment)
        self.assertEqual(self.enrollment.student, self.student)
        self.assertEqual(self.enrollment.course, self.course)
        self.assertEqual(self.enrollment.points_assigned, 3.0)
        self.assertFalse(self.enrollment.is_waitlisted)

    def test_enrollment_unique_constraint(self):
        # Attempt to create a duplicate enrollment
        with self.assertRaises(Exception) as context:
            Enrollment.objects.create(
                student=self.student,
                course=self.course,
                points_assigned=3.0,
                is_waitlisted=False
            )
        self.assertTrue('UNIQUE constraint failed' in str(context.exception))

    def test_enrollment_string_representation(self):
        expected_str = f'{self.student.Name} enrolled in {self.course.name}'
        self.assertEqual(str(self.enrollment), expected_str)
