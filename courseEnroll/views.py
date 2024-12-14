from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import transaction
from django.contrib import messages
from userprofile.models import StudentInfo
from .models import CourseInfo, Enrollment
from .forms import OverrideFormSubmission, PreRegInfoForm
from courseEnroll.models import OverrideForm, PreRegInfo
from django.shortcuts import get_object_or_404
from django.utils import timezone
import json  # Add this import
from django.core.serializers.json import DjangoJSONEncoder  # Add this too if not already present
from datetime import datetime


@login_required
def dashboard(request):
    try:
        inconsistencies = verify_course_enrollment_consistency()

        try:
            student_info = StudentInfo.objects.get(user=request.user)
        except StudentInfo.DoesNotExist:
            return render(request, "userprofile/student_not_found.html", {"error": "Student profile not found."})
        
        student_department = student_info.department
        max_points = 100
        max_credits = 12

        # Calculate total credits and points
        total_enrolled_credits = float(sum(
            enrollment.course.credits 
            for enrollment in student_info.enrollments.filter(is_waitlisted=False)
        ))
        
        remaining_credits = max_credits - total_enrolled_credits

        total_waitlist_points = float(sum(
            float(enrollment.points_assigned or 0)
            for enrollment in student_info.enrollments.filter(is_waitlisted=True)
        ))
        
        remaining_points = max_points - total_waitlist_points

        all_enrollments = student_info.enrollments.all()
        
        # Prepare course data with explicit float conversion
        enrolled_courses = [
            {
                'course': {
                    'course_id': str(enrollment.course.course_id),
                    'name': str(enrollment.course.name),
                    'credits': float(enrollment.course.credits),
                    'description': str(enrollment.course.description),
                    'class_days':str(enrollment.course.class_days),
                    'Instructor': {
                        'Name': str(enrollment.course.Instructor.Name)
                    },
                    'start_time': str(enrollment.course.start_time),
                    'end_time': str(enrollment.course.end_time)
                },
                'created_at': str(enrollment.created_at)
            }
            for enrollment in all_enrollments if not enrollment.is_waitlisted
        ]

        waitlist_courses = []
        for enrollment in all_enrollments:
            if enrollment.is_waitlisted:
                course_waitlist = list(Enrollment.objects.filter(
                    course=enrollment.course, 
                    is_waitlisted=True
                ).order_by('-true_points'))
                
                try:
                    position = next(
                        (index + 1 for index, e in enumerate(course_waitlist) 
                         if e.id == enrollment.id), 
                        None
                    )
                except Exception as e:
                    print(f"Error finding position: {e}")
                    position = None

                waitlist_courses.append({
                    'course': {
                        'course_id': str(enrollment.course.course_id),
                        'name': str(enrollment.course.name),
                        'credits': float(enrollment.course.credits),
                        'description': str(enrollment.course.description),
                        'Instructor': {
                            'name': str(enrollment.course.Instructor.Name)
                        },
                        'start_time': str(enrollment.course.start_time),
                        'end_time': str(enrollment.course.end_time),
                        'position': position,
                        'total_waitlist': len(course_waitlist)
                    },
                    'points_assigned': float(enrollment.points_assigned if enrollment.points_assigned is not None else 0),
                    'true_points': float(enrollment.true_points if enrollment.true_points is not None else 0),
                    'created_at': str(enrollment.created_at)
                })

        # Convert to JSON after explicit float conversion
        enrolled_courses_json = json.dumps(enrolled_courses)
        waitlist_courses_json = json.dumps(waitlist_courses)

        context = {
            'student_info': student_info,
            'points_left': float(remaining_points),
            'credits_left': float(remaining_credits),
            'enrolled_courses': enrolled_courses,
            'waitlist_courses': waitlist_courses,
            'enrolled_courses_json': enrolled_courses_json,
            'waitlist_courses_json': waitlist_courses_json,
            'override_form_submissions': OverrideForm.objects.filter(student=student_info),
            'override_form': OverrideFormSubmission(user=request.user),
            'prereg_form': None if PreRegInfo.objects.filter(student_id=student_info).exists() else PreRegInfoForm(user=request.user),
            'prereg_form_exists': PreRegInfo.objects.filter(student_id=student_info).exists(),
            'inconsistencies': inconsistencies,
        }

        return render(request, 'courseEnroll/dashboard.html', context)
    except Exception as e:
        print(f"Error in dashboard: {str(e)}")
        # Return a response even if there's an error
        return render(request, 'courseEnroll/dashboard.html', {
            'error': f"An error occurred: {str(e)}"
        })

@login_required
def swap_courses(request):
    if request.method == 'POST':
        enrolled_course_id = request.POST.get('enrolled_course_id')
        waitlisted_course_id = request.POST.get('waitlisted_course_id')
        
        if not enrolled_course_id or not waitlisted_course_id:
            messages.error(request, "Please select both courses to swap.")
            return redirect('courseEnroll:dashboard')

        student_info = request.user.studentinfo

        try:
            with transaction.atomic():
                # Get both enrollments
                enrolled = Enrollment.objects.get(
                    student=student_info,
                    course__course_id=enrolled_course_id,
                    is_waitlisted=False
                )
                waitlisted = Enrollment.objects.get(
                    student=student_info,
                    course__course_id=waitlisted_course_id,
                    is_waitlisted=True
                )

                # Store course references before deletion
                enrolled_course = enrolled.course
                waitlisted_course = waitlisted.course
                points_to_refund = waitlisted.points_assigned or 0

                # Remove enrolled course from both models
                student_info.course_enrolled.remove(enrolled_course)
                enrolled.delete()

                # Delete waitlist enrollment
                waitlisted.delete()

                # Create new enrollment and add to course_enrolled
                new_enrollment = Enrollment.objects.create(
                    student=student_info,
                    course=waitlisted_course,
                    is_waitlisted=False,
                    points_assigned=0
                )
                student_info.course_enrolled.add(waitlisted_course)

                # Update student info
                student_info.points = student_info.points + points_to_refund
                
                # Update course capacities
                if student_info.Education_Level == "Graduate":
                    waitlisted_course.grad_Capacity -= 1
                else:
                    waitlisted_course.phd_course_capacity -= 1

                # Save changes
                waitlisted_course.save()
                student_info.save()

                messages.success(request, f"Successfully swapped {enrolled_course.name} with {waitlisted_course.name}")

        except Enrollment.DoesNotExist:
            messages.error(request, "One or both selected courses were not found.")
        except Exception as e:
            messages.error(request, f"Error swapping courses: {str(e)}")

    return redirect('courseEnroll:dashboard')


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
    target_date = timezone.make_aware(datetime(2024, 12, 12, 0, 0, 0))

    if request.method == 'POST':
        student_info = StudentInfo.objects.get(user=request.user)
        student_school = student_info.School
        student_points = student_info.points
        student_department = student_info.department
        selected_courses = request.POST.getlist('selected_courses')
        edu_level = student_info.Education_Level

        # Calculate current total enrolled credits
        current_enrolled_credits = sum(
            enrollment.course.credits 
            for enrollment in student_info.enrollments.filter(is_waitlisted=False)
        )

        action = request.POST.get('action', 'enroll')

        with transaction.atomic():
            for course_id in selected_courses:
                course = CourseInfo.objects.get(course_id=course_id)
                course_credits = course.credits

                # Check if enrolling this course would exceed 12 credits
                if action == 'enroll' and (current_enrolled_credits + course_credits) > 12:
                    messages.error(request, f"Cannot enroll in {course.name}: Enrolling would exceed the 12 credit limit.")
                    continue

                # Check school match
                if course.school != student_school:
                    messages.error(request, f"{course.name} is not offered by your school ({student_school}). Please contact your advisor.")
                    continue

                # Check department match
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

                # Determine capacity based on education level
                capacity = course.grad_Capacity if edu_level == "Graduate" else course.phd_course_capacity

                # Handle waitlisted enrollments
                waitlisted_enrollment = Enrollment.objects.filter(
                    student=student_info, course=course, is_waitlisted=True
                ).first()

                if action == 'enroll':
                    # Check if already enrolled
                    if Enrollment.objects.filter(student=student_info, course=course, is_waitlisted=False).exists():
                        messages.warning(request, f"You are already enrolled in {course.name}.")
                        continue

                    if capacity <= 0:
                        messages.error(request, f"Cannot enroll in {course.name}: No capacity available.")
                        continue

                    if waitlisted_enrollment:
                        # Move from waitlist to enrolled
                        waitlisted_enrollment.is_waitlisted = False
                        waitlisted_enrollment.points_assigned = None
                        waitlisted_enrollment.save()
                        student_info.course_enrolled.add(course)


                        # Refund points if any were assigned
                        if waitlisted_enrollment.points_assigned:
                            student_info.points += waitlisted_enrollment.points_assigned

                    else:
                        # Direct enrollment
                        Enrollment.objects.create(student=student_info, course=course, is_waitlisted=False)
                        student_info.course_enrolled.add(course)



                    # Update course capacity
                    if edu_level == "Graduate":
                        course.grad_Capacity -= 1
                    else:
                        course.phd_course_capacity -= 1
                    course.save()

                    # Update student's enrolled courses and credits
                    student_info.course_enrolled.add(course)
                    current_enrolled_credits += course_credits
                    student_info.save()

                    messages.success(request, f"Successfully enrolled in {course.name}.")

                elif action == 'waitlist':
                    if not waitlisted_enrollment:
                        points_assigned = request.POST.get(f'points_{course_id}', 0)
                        try:
                            print(f"Current student points: {student_info.points}")
                            print(f"Points attempting to assign: {points_assigned}")
                            print(f"Calculation check: 100 - {student_info.points} = {100 -int(points_assigned)}")

                            points_assigned = int(points_assigned)
                            
                            if points_assigned < 0:
                                messages.error(request, f"Points cannot be negative for {course.name}")
                                continue
                            
                            if points_assigned > student_points:
                                messages.error(request,
                                    f"Not enough points available for {course.name}. "
                                    f"Current points: {student_points}, "
                                    f"Attempted to assign: {points_assigned}"
                                )
                                continue

                            new_enrollment = Enrollment.objects.create(
                                student=student_info, 
                                course=course, 
                                is_waitlisted=True,
                                points_assigned=points_assigned
                            )

                            days_difference = max(0, (new_enrollment.created_at - target_date).days)
                            true_points = max(0, points_assigned - (days_difference * 1.6))
                            
                            new_enrollment.true_points = true_points
                            new_enrollment.save()

                            student_info.points -= points_assigned
                            student_info.save()

                            messages.success(request, 
                                f"Successfully waitlisted for {course.name} with {points_assigned} points. "
                                f"True points for position: {true_points}"
                            )
                        except ValueError:
                            messages.error(request, f"Invalid points value for {course.name}.")
                            continue
                    else:
                        messages.error(request, f"You are already waitlisted for {course.name}.")

    return redirect('courseEnroll:dashboard')

@login_required
def delete_selected_courses(request):
    if request.method == 'POST':
        selected_courses = request.POST.getlist('selected_courses')
        if selected_courses:
            with transaction.atomic():  # Add transaction
                for course_id in selected_courses:
                    try:
                        # Get both student and enrollment
                        student_info = request.user.studentinfo
                        enrollment = Enrollment.objects.get(
                            student=student_info, 
                            course__course_id=course_id
                        )
                        
                        # Remove from both models
                        student_info.course_enrolled.remove(enrollment.course)
                        enrollment.delete()

                        messages.success(request, f"Course {enrollment.course.name} successfully removed.")
                    except Enrollment.DoesNotExist:
                        messages.error(request, f"Enrollment for course ID {course_id} does not exist.")
                    except Exception as e:
                        messages.error(request, f"An error occurred: {e}")

    return redirect('courseEnroll:dashboard')

@login_required
def delete_course(request, course_id):
    # Fetch the course to delete
    course = get_object_or_404(CourseInfo, id=course_id)
    
    # Handle Enrollments (delete all enrollments associated with the course)
    enrollments = Enrollment.objects.filter(course=course)
    enrollments.delete()
    
    # Remove the course from students' course_enrolled ManyToMany field
    students = StudentInfo.objects.filter(course_enrolled=course)
    for student in students:
        student.course_enrolled.remove(course)

    # Check if this course is any student's TA course and unset it
    StudentInfo.objects.filter(ta_course=course).update(ta_course=None)

    # Finally, delete the course
    course.delete()

    # Provide feedback to the user
    messages.success(request, f"Course '{course.name}' has been successfully deleted.")
    return redirect('courses_list') 

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
                request.user.studentinfo.points_left += enrollment.points_assigned  # Revert the points deduction for waitlist
            else:
                request.user.studentinfo.course_enrolled.add(enrollment.course)
                request.user.studentinfo.points_left -= enrollment.points_assigned  # Deduct points for enrolling in the course
            
            request.user.studentinfo.save()

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

    print("\n=== Course Enrollment Consistency Check ===")  # Added header for clarity

    for student in StudentInfo.objects.annotate(enrolled_count=Count('course_enrolled')):
        course_enrolled_ids = set(student.course_enrolled.values_list('course_id', flat=True))
        enrollment_course_ids = set(student.enrollments.filter(is_waitlisted=False).values_list('course__course_id', flat=True))
        
        print(f"\nChecking student: {student.Name} (ID: {student.N_id})")
        print(f"Courses in course_enrolled: {course_enrolled_ids}")
        print(f"Courses in enrollments: {enrollment_course_ids}")

        if course_enrolled_ids != enrollment_course_ids:
            mismatches[student.N_id] = {
                'course_enrolled_ids': course_enrolled_ids,
                'enrollment_course_ids': enrollment_course_ids,
                'difference': {
                    'in_course_enrolled_not_in_enrollments': course_enrolled_ids - enrollment_course_ids,
                    'in_enrollments_not_in_course_enrolled': enrollment_course_ids - course_enrolled_ids,
                }
            }
    
    print("\n=== Consistency Check Results ===")
    if not mismatches:
        print("✓ All student course data is consistent.")
    else:
        print("❌ Inconsistencies found. See details below:")
        for student_id, details in mismatches.items():
            print(f"\nStudent ID: {student_id}")
            print(f"  - Courses in course_enrolled but not in Enrollment: {details['difference']['in_course_enrolled_not_in_enrollments']}")
            print(f"  - Courses in Enrollment but not in course_enrolled: {details['difference']['in_enrollments_not_in_course_enrolled']}")
    
    print("\n=====================================")
    return mismatches

def submit_override_form(request):
    pass

from .models import CourseInfo, Enrollment

