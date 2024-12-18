from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from userprofile.models import DepartmentInfo,FacultyInfo,StudentInfo
from django.http import HttpResponse,JsonResponse
from courseEnroll.models import CourseInfo, OverrideForm,PreRegInfo
from datetime import date,datetime
from django.contrib import messages
from courseEnroll.forms import OverrideFormSubmission
from django.db.models import Q
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

email_address = "alper.mumcular@ug.bilkent.edu.tr"
email_password = "Enroll@123"

smtp_server = "asmtp.bilkent.edu.tr"
smtp_port = 587  # STARTTLS Port
print(os.getenv("DEBUG"))

def admin_required(user):
    return user.is_superuser

# Create your views here.
@login_required
@user_passes_test(admin_required)
def admin_dashboard(request):
    departments = DepartmentInfo.objects.all()
    courses = CourseInfo.objects.all()

    return render(request, 'systemadmin/admin_dashboard.html', {'departments': departments, 'courses': courses})

@login_required
@user_passes_test(admin_required)
def prereg(request):
    prereg_data = dict()
    courses = CourseInfo.objects.all()
    for course in courses:
        prereg_data[course.course_id] = dict()
        prereg_data[course.course_id]["course_id"] = course.course_id
        prereg_data[course.course_id]["name"] = course.name
        prereg_data[course.course_id]["Department"] = course.Department.name
        prereg_data[course.course_id]["capacity"] = course.undergrad_capacity + course.grad_Capacity + course.phd_course_capacity
        course_count = PreRegInfo.objects.filter(
            Q(course1=course) | Q(course2=course) | Q(course3=course)
        ).count()

        prereg_data[course.course_id]["request"] = course_count

    return render(request, 'systemadmin/preregistration.html', {'prereg_data': prereg_data})

@login_required
@user_passes_test(admin_required)

def override(request):
    # Query all override form submissions
    override_forms = OverrideForm.objects.all()

    # Pass the data to the template
    return render(request, 'systemadmin/override.html', {'override_forms': override_forms})


def modify_override(request):
    if request.method == 'POST':
        status = request.POST.get('action')  # Approved/Rejected
        formId = request.POST.get('formId')  # The form ID

        # Fetch the specific override form based on formId
        override_form = get_object_or_404(OverrideForm, form_id=formId)

        recipient_email = "am14533@nyu.edu"  # Replace with the recipient's email
        subject = "Override Form Status Update"
        body = f"""
                <html>
                    <body>
                        <p>Your override request for <strong>{override_form.course_code}</strong> has been <strong>{status.lower()}</strong>.</p>
                        <p>To see your current courses, click <a href='http://127.0.0.1:8000/userprofile/login/'>here</a>.</p>
                    </body>
                </html>
                """

        message = MIMEMultipart()
        message["From"] = "NYU Enrolls <alper.mumcular@ug.bilkent.edu.tr>"  # Custom "From" name
        message["To"] = recipient_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))  # Use "html" instead of "plain"

        try:
            # Connect to the SMTP server
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                # Start TLS for security
                server.starttls()
                # Login to the email account
                server.login(email_address, email_password)
                # Send the email
                server.sendmail(email_address, recipient_email, message.as_string())
                print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")

        # Update the status of the form
        override_form.status = status
        override_form.save()

    return redirect('systemadmin:override')


def logout_request(request):
    logout(request)
    return redirect('userprofile:login')

def course_add(request):
    if request.method == 'POST':
        course_id = request.POST.get('courseId')
        course_name = request.POST.get('courseName')
        department_code = request.POST.get('department')
        capacity = request.POST.get('capacity', '0')
        phd_seats = request.POST.get('phdSeats', '0')
        class_day = request.POST.get('classDay')
        start_time = request.POST.get('startTime')  # Fetch the start time
        end_time = request.POST.get('endTime')      # Fetch the end time
        course_description = request.POST.get('courseDescription')
        credits = request.POST.get('credits', '0')
        section = request.POST.get('section')
        waitlist_capacity = request.POST.get('waitlistCapacity', '0')

        try:
            # Validate start_time and end_time
            start_time_parsed = datetime.strptime(start_time, '%H:%M').time() if start_time else None
            end_time_parsed = datetime.strptime(end_time, '%H:%M').time() if end_time else None

            if not start_time_parsed or not end_time_parsed:
                messages.error(request, "Start time and end time are required.")
                return redirect('systemadmin:dashboard')

            # Fetch related department
            department = get_object_or_404(DepartmentInfo, department_id=department_code)

            # Create the course
            CourseInfo.objects.create(
                course_id=course_id,
                name=course_name,
                Department=department,
                undergrad_capacity=int(capacity),
                phd_course_capacity=int(phd_seats),
                class_days=class_day,
                start_time=start_time_parsed,
                end_time=end_time_parsed,
                description=course_description,
                credits=float(credits),
                section=section,
                grad_Capacity=0,  # Adjust as per your logic
            )
            messages.success(request, "Course has been added successfully!")
        except Exception as e:
            messages.error(request, f"Error adding course: {str(e)}")

        return redirect('systemadmin:dashboard')

    return HttpResponse("Invalid Request", status=400)



def course_update(request):
    if request.method == 'POST':
        course_id = request.POST.get('courseId')
        course = get_object_or_404(CourseInfo, course_id=course_id)

        try:
            # Update course fields
            course.name = request.POST.get('courseName')
            course.Department = get_object_or_404(DepartmentInfo, department_id=request.POST.get('department'))

            # Get the instructor name from the form
            instructor_name = request.POST.get('instructor')

            # Fetch the FacultyInfo instance by name
            instructor = FacultyInfo.objects.filter(Name=instructor_name).first()

            if not instructor:
                raise ValueError(f"Instructor '{instructor_name}' not found in the database.")

            course.Instructor = instructor
            course.undergrad_capacity = int(request.POST.get('undergradCapacity', 0))
            course.grad_Capacity = int(request.POST.get('gradCapacity', 0))
            course.phd_course_capacity = int(request.POST.get('phdSeats', 0))
            course.section = request.POST.get('section')
            course.class_days = request.POST.get('classDay')
            course.start_time = request.POST.get('startTime')
            course.end_time = request.POST.get('endTime')
            course.description = request.POST.get('courseDescription')
            course.to_waitlist = bool(request.POST.get('toWaitlist'))
            course.points_assigned = int(request.POST.get('pointsAssigned', 0))
            course.credits = float(request.POST.get('credits', 0))
            course.waitlist_capacity = int(request.POST.get('waitlistCapacity', 0))

            # Save updated course
            course.save()

            messages.success(request, "Course updated successfully!")
        except Exception as e:
            messages.error(request, f"Error updating course: {str(e)}")

        return redirect('systemadmin:dashboard')

    return HttpResponse("Invalid Request", status=400)

def get_course_details(request, course_id):
    if request.method == 'GET':
        # Fetch the course from the database
        course = get_object_or_404(CourseInfo, course_id=course_id)

        # Return the course details as JSON
        return JsonResponse({
            'course_id': course.course_id,
            'name': course.name,
            'department_id': course.Department.department_id if course.Department else '',
            'Instructor': course.Instructor.Name if course.Instructor else '',
            'undergrad_capacity': course.undergrad_capacity,
            'grad_capacity': course.grad_Capacity,
            'phd_course_capacity': course.phd_course_capacity,
            'section': course.section,
            'class_days': course.class_days,
            'start_time': course.start_time.strftime('%H:%M') if course.start_time else '',
            'end_time': course.end_time.strftime('%H:%M') if course.end_time else '',
            'description': course.description,
            'to_waitlist': course.to_waitlist,
            'points_assigned': course.points_assigned,
            'credits': float(course.credits),
            'waitlist_capacity': course.waitlist_capacity,
        })
    return JsonResponse({'error': 'Invalid request method'}, status=400)
def delete_course(request, course_id):
    if request.method == 'POST':
        try:
            # Fetch the course using course_id
            course = get_object_or_404(CourseInfo, course_id=course_id)

            # Delete the course
            course.delete()

            return JsonResponse({'message': 'Course deleted successfully!'}, status=200)
        except Exception as e:
            return JsonResponse({'error': f'Error deleting course: {str(e)}'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)
