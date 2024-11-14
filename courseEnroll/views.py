from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from userprofile.models import StudentInfo
from .models import CourseInfo, Enrollment

@login_required
def dashboard(request):
    student_info = StudentInfo.objects.get(user=request.user)
    all_enrollments = student_info.enrollments.all()
    enrolled_courses = [
        {'course': enrollment.course, 'created_at': enrollment.created_at} 
        for enrollment in all_enrollments if not enrollment.is_waitlisted
    ]
    waitlist_courses = [
        {'course': enrollment.course, 'created_at': enrollment.created_at} 
        for enrollment in all_enrollments if enrollment.is_waitlisted
    ]

    return render(request, 'courseEnroll/dashboard.html', {
        'student_info': student_info,
        'enrolled_courses': enrolled_courses,
        'waitlist_courses': waitlist_courses,
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
        student_school =  student_info.School
        selected_courses = request.POST.getlist('selected_courses')
        edu_level = request.user.studentinfo.Education_Level
        total_credits = sum(enrollment.course.credits for enrollment in request.user.studentinfo.enrollments.filter(is_waitlisted=False))
        action = request.POST.get('action', 'enroll')

        for course_id in selected_courses:
            course = CourseInfo.objects.get(course_id=course_id)
            course_school = course.school
            credit = course.credits

            

            if edu_level == "Undergraduate":
                capacity = course.undergrad_capacity
            elif edu_level == "Graduate":
                capacity = course.grad_Capacity
            else:
                capacity = course.phd_course_capacity

            is_waitlisted = Enrollment.objects.filter(
                student=request.user.studentinfo,
                course=course,
                is_waitlisted=True
            ).exists()

            if is_waitlisted:
                messages.error(request, f"You are already waitlisted for the course: {course.name}.")
                continue

            if action == 'waitlist' and not is_waitlisted:
                
                    if not Enrollment.objects.filter(student=request.user.studentinfo, course=course, is_waitlisted=False).exists():
                        Enrollment.objects.create(student=request.user.studentinfo, course=course, is_waitlisted=True)
                        request.user.studentinfo.course_enrolled.add(course)
                        messages.success(request, f"You have been added to the waitlist for {course.name}.")
                    else:
                        messages.error(request, f"You are already enrolled in {course.name}.")
               

            elif action == 'enroll':
                if (Enrollment.objects.filter(student=request.user.studentinfo, course=course, is_waitlisted=False).exists() 
                or course in request.user.studentinfo.course_enrolled.all()):
        
                    messages.warning(request, f"You are already enrolled in {course.name}.")
                    continue
                if total_credits + credit <= 9:
                    if course.grad_Capacity > 0:
                        Enrollment.objects.create(student=request.user.studentinfo, course=course, is_waitlisted=False)
                        request.user.studentinfo.course_enrolled.add(course)
                        total_credits += credit
                        
                        if edu_level == "Undergraduate":
                            course.undergrad_capacity -= 1
                        elif edu_level == "Graduate":
                            course.grad_Capacity -= 1
                        else:
                            course.phd_course_capacity -= 1
                        
                        course.save()
                    else:
                        if course.to_waitlist:
                            Enrollment.objects.create(student=request.user.studentinfo, course=course, is_waitlisted=True)
                            request.user.studentinfo.course_enrolled.add(course)
                            messages.success(request, f"You have been added to the waitlist for {course.name}.")
                        else:
                            messages.error(request, f"The current capacity for {course.name} has been filled. Try to waitlist instead.")
                else:
                    messages.error(request, "You have reached your course credit limit of 9.")

    return redirect('courseEnroll:dashboard')

@login_required
def delete_selected_courses(request):
    if request.method == 'POST':
        selected_courses = request.POST.getlist('selected_courses')
        if selected_courses:
            for course_id in selected_courses:
                try:
                    # Retrieve the Enrollment instance first
                    enrollment = Enrollment.objects.get(student=request.user.studentinfo, course__course_id=course_id)
                    
                    # Delete the enrollment entry (removes the student-course relationship)
                    enrollment.delete()

                    # If you want to ensure that the student is removed from the course's enrolled students, remove the course as well
                    # This is for a better sync in case any other places depend on `course_enrolled`
                    request.user.studentinfo.course_enrolled.remove(enrollment.course)

                except Enrollment.DoesNotExist:
                    pass  # If no enrollment found, simply skip the course

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