from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import transaction
from django.contrib import messages
from userprofile.models import StudentInfo
from .models import CourseInfo, Enrollment
from .forms import OverrideFormSubmission,PreRegInfoForm
from courseEnroll.models import OverrideForm,PreRegInfo
from django.shortcuts import get_object_or_404

@login_required
def dashboard(request):
    try:
        student_info = StudentInfo.objects.get(user=request.user)
    except StudentInfo.DoesNotExist:
        return render(request, "userprofile/student_not_found.html", {"error": "Student profile not found."})
    
    student_department = student_info.department
    student_points  =student_info.points
    student_credits =  student_info.credits_left
    print("Students credits")
    all_enrollments = student_info.enrollments.all()
    courses = CourseInfo.objects.filter(Department=student_department)

    enrolled_courses = [
        {'course': enrollment.course, 'created_at': enrollment.created_at} 
        for enrollment in all_enrollments if not enrollment.is_waitlisted
    ]
    waitlist_courses = [
        {'course': enrollment.course, 'created_at': enrollment.created_at} 
        for enrollment in all_enrollments if enrollment.is_waitlisted
    ]

    inconsistencies = verify_course_enrollment_consistency()
    override_form_submissions = OverrideForm.objects.filter(student=student_info)

    prereg_form_exists = PreRegInfo.objects.filter(student_id=student_info).exists()

    # Initialize forms
    override_form = OverrideFormSubmission(user=request.user)
    prereg_form = None if prereg_form_exists else PreRegInfoForm(user=request.user)

    # Handle POST requests
    if request.method == "POST":
        if 'override_form' in request.POST:
            override_form = OverrideFormSubmission(request.POST, user=request.user)
            if override_form.is_valid():
                override_instance = override_form.save(commit=False)
                override_instance.student = student_info
                override_instance.save()
                return redirect('courseEnroll:dashboard')  # Refresh the page
        elif 'prereg_form' in request.POST and not prereg_form_exists:
            prereg_form = PreRegInfoForm(request.POST, user=request.user)
            if prereg_form.is_valid():
                prereg_instance = prereg_form.save(commit=False)
                prereg_instance.student_id = student_info
                prereg_instance.save()
                return redirect('courseEnroll:dashboard')  # Refresh the page

    return render(request, 'courseEnroll/dashboard.html', {
        'student_info': student_info,
        'points_left': student_points,
        'credits_left':credits,
        'courses': courses,
        'inconsistencies': inconsistencies,
        'enrolled_courses': enrolled_courses,
        'waitlist_courses': waitlist_courses,
        'override_form_submissions': override_form_submissions,
        'override_form': override_form,
        'prereg_form': prereg_form,
    })

@login_required
def search_courses(request):
    if request.method == 'POST':
        search_courses = request.POST.get('search_courses', '')
        action = request.POST.get('action', 'enroll')
        
        courses = CourseInfo.objects.filter(
            Q(course_id__icontains=search_courses) |
            Q(name__icontains=search_courses) | 
            Q(description__icontains=search_courses) |  
            Q(Instructor__Name__icontains=search_courses)
        )
        return render(request, 'courseEnroll/course_search.html', {
            'search_courses': search_courses,
            'courses': courses,
            'action': action
        })
    else:
        return render(request, 'courseEnroll/course_search.html', {})

@login_required
def select_courses(request):
    if request.method == 'POST':
        student_info = StudentInfo.objects.get(user=request.user)
        student_school = student_info.School
        student_points  =student_info.points
        student_credits =  student_info.credits_left
        student_department = student_info.department
        selected_courses = request.POST.getlist('selected_courses')
        edu_level = student_info.Education_Level
        total_credits = sum(
            enrollment.course.credits 
            for enrollment in student_info.enrollments.filter(is_waitlisted=False)
        )
        action = request.POST.get('action', 'enroll')

        with transaction.atomic():  
            for course_id in selected_courses:
                course = CourseInfo.objects.get(course_id=course_id)
                credit = course.credits

                print(f"Checking course: {course.name}, Capacity: {course.undergrad_capacity if edu_level == 'Undergraduate' else course.grad_Capacity if edu_level == 'Graduate' else course.phd_course_capacity}")
                
                if course.school != student_school:
                    messages.error(request, f"{course.name} is not offered by your school ({student_school}). Please contact your advisor.")
                    continue
                
                if course.Department != student_department:
                    override = OverrideForm.objects.filter(
                        student=student_info, course_code=course, status='Approved'
                    ).first()

                    if not override:
                        messages.error(
                            request,
                            f"{course.name} is not in your department ({student_department.name}). "
                            "Please submit an override request and wait for approval before enrolling."
                        )
                        continue

                if edu_level == "Graduate":
                    capacity = course.grad_Capacity
                else:
                    capacity = course.phd_course_capacity

                is_waitlisted = Enrollment.objects.filter(
                    student=student_info, course=course, is_waitlisted=True
                ).exists()
                print(f"Is {course.name} already waitlisted? {is_waitlisted}")

                if is_waitlisted:
                    messages.error(request, f"You are already waitlisted for {course.name}.")
                    continue

                if action == 'waitlist' and not is_waitlisted:
                    if not Enrollment.objects.filter(student=student_info, course=course, is_waitlisted=False).exists():
                        Enrollment.objects.create(student=student_info, course=course, is_waitlisted=True)
                        student_info.course_enrolled.add(course)
                        messages.success(request, f"You have been added to the waitlist for {course.name}.")
                    else:
                        messages.error(request, f"You are already enrolled in {course.name}.")
                elif action == 'enroll':
                    if (Enrollment.objects.filter(student=student_info, course=course, is_waitlisted=False).exists() 
                        or course in student_info.course_enrolled.all()):
                        messages.warning(request, f"You are already enrolled in {course.name}.")
                        continue
                    
                    if total_credits + credit <= 12:
                        if capacity > 0:
                            Enrollment.objects.create(student=student_info, course=course, is_waitlisted=False)
                            student_info.course_enrolled.add(course)
                            total_credits += credit
                            if edu_level == "Graduate":
                                course.grad_Capacity -= 1
                            else:
                                course.phd_course_capacity -= 1
                            course.save()
                            messages.success(request, f"Successfully enrolled in {course.name}.")
                        else:
                            if course.to_waitlist:
                                Enrollment.objects.create(student=student_info, course=course, is_waitlisted=True)
                                student_info.course_enrolled.add(course)
                                messages.success(request, f"You have been added to the waitlist for {course.name}.")
                            else:
                                messages.error(request, f"Capacity for {course.name} is full. Try waitlisting.")
                    else:
                        messages.error(request, "You have reached your course credit limit of 9.")

        student_info.save()

    return redirect('courseEnroll:dashboard')

@login_required
def delete_selected_courses(request):
    if request.method == 'POST':
        selected_courses = request.POST.getlist('selected_courses')
        if selected_courses:
            for course_id in selected_courses:
                try:
                    enrollment = Enrollment.objects.get(student=request.user.studentinfo, course__course_id=course_id)  
                    request.user.studentinfo.course_enrolled.remove(enrollment.course)
                    enrollment.delete()

                    messages.success(request, f"Course {enrollment.course.name} successfully removed.")
                except Enrollment.DoesNotExist:
                    messages.error(request, f"Enrollment for course ID {course_id} does not exist.")
                except Exception as e:
                    messages.error(request, f"An error occurred: {e}")

    return redirect('courseEnroll:dashboard')

@login_required
def update_enrollment(request):
    if request.method == 'POST':
        for enrollment in request.user.studentinfo.enrollments.all():
            course_id = enrollment.course.course_id
            waitlist = request.POST.get(f'waitlist_{course_id}') == 'on'
            points = request.POST.get(f'points_{course_id}', '')

            enrollment.is_waitlisted = waitlist
            enrollment.points_assigned = points
            enrollment.save()

            if waitlist:
                request.user.studentinfo.course_enrolled.remove(enrollment.course)
            else:
                request.user.studentinfo.course_enrolled.add(enrollment.course)

    return redirect('courseEnroll:dashboard')


def course_enrollment(request, course_id):
    course = CourseInfo.objects.get(course_id=course_id)
    enrollments_records= course.enrollments.values('student__Name', 'created_at', 'points_assigned','is_waitlisted').order_by('points_assigned')
    waitlist_record = enrollments_records.filter(is_waitlisted=True)
    context = {
        'course': course,
        'enrollments': waitlist_record
    }
    return render(request, 'courseEnroll/course_enrollment.html', context)


from django.db.models import Count

def verify_course_enrollment_consistency():
   
    mismatches = {}

    for student in StudentInfo.objects.annotate(enrolled_count=Count('course_enrolled')):
        course_enrolled_ids = set(student.course_enrolled.values_list('course_id', flat=True))
        
        enrollment_course_ids = set(student.enrollments.values_list('course__course_id', flat=True))
        
        if course_enrolled_ids != enrollment_course_ids:
            mismatches[student.N_id] = {
                'course_enrolled_ids': course_enrolled_ids,
                'enrollment_course_ids': enrollment_course_ids,
                'difference': {
                    'in_course_enrolled_not_in_enrollments': course_enrolled_ids - enrollment_course_ids,
                    'in_enrollments_not_in_course_enrolled': enrollment_course_ids - course_enrolled_ids,
                }
            }
    
    if not mismatches:
        print("All student course data is consistent.")
    else:
        print("Inconsistencies found. See details below:")
        for student_id, details in mismatches.items():
            print(f"Student ID: {student_id}")
            print(f"  - Courses in `course_enrolled` but not in `Enrollment`: {details['difference']['in_course_enrolled_not_in_enrollments']}")
            print(f"  - Courses in `Enrollment` but not in `course_enrolled`: {details['difference']['in_enrollments_not_in_course_enrolled']}")
    
    return mismatches

def submit_override_form(request):
    pass