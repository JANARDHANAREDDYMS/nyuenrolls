from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import transaction
from django.contrib import messages
from userprofile.models import StudentInfo,DepartmentInfo
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

        # Handle PreRegInfo Form Submission
        if request.method == 'POST':
            prereg_form = PreRegInfoForm(request.POST, user=request.user)
            if prereg_form.is_valid():
                # Check if pre-registration already exists
                existing_prereg = PreRegInfo.objects.filter(student_id=student_info).first()
                
                if existing_prereg:
                    messages.warning(request, "You have already submitted a pre-registration form.")
                else:
                    # Save the pre-registration form
                    prereg_instance = prereg_form.save(commit=False)
                    prereg_instance.student_id = student_info
                    prereg_instance.save()
                    
                    messages.success(request, "Pre-registration submitted successfully!")
                
                return redirect('courseEnroll:dashboard')
            else:
                # If form is not valid, print errors (for debugging)
                print(prereg_form.errors)

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
                    'class_days': str(enrollment.course.class_days),
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
                        'class_days': str(enrollment.course.class_days),
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
                
                # Check course capacity based on student's education level
                if student_info.Education_Level == "Graduate":
                    if waitlisted_course.grad_Capacity <= 0:
                        messages.error(request, f"Cannot swap: {waitlisted_course.name} has no available graduate seats.")
                        return redirect('courseEnroll:dashboard')
                else:
                    if waitlisted_course.phd_course_capacity <= 0:
                        messages.error(request, f"Cannot swap: {waitlisted_course.name} has no available PhD seats.")
                        return redirect('courseEnroll:dashboard')
                
                # Convert points to a consistent type (float)
                points_to_refund = float(waitlisted.points_assigned or 0)
                
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
                # Convert student_info.points to float if it's a Decimal
                student_points = float(student_info.points)
                student_info.points = student_points + points_to_refund
                
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
        student_info = StudentInfo.objects.get(user=request.user)
        
        # Calculate remaining points using the same method as in dashboard
        total_waitlist_points = float(sum(
            float(enrollment.points_assigned or 0)
            for enrollment in student_info.enrollments.filter(is_waitlisted=True)
        ))
        
        # Calculate remaining points
        remaining_points = 100 - total_waitlist_points
        
        # Debug print
        print(f"Total Waitlisted Points: {total_waitlist_points}")
        print(f"Calculated Remaining Points: {remaining_points}")
        
        search_courses = request.POST.get('search_courses', '')
        school_id = request.POST.get('school', '')
        department_id = request.POST.get('department', '')
        action = request.POST.get('action', 'enroll')

        courses = CourseInfo.objects.all()

        # Existing filtering logic...
        if school_id:
            courses = courses.filter(school__id=school_id)

        if department_id:
            courses = courses.filter(Department__id=department_id)

        courses = CourseInfo.objects.filter(
            Q(course_id__icontains=search_courses) |
            Q(name__icontains=search_courses) | 
            Q(description__icontains=search_courses) |  
            Q(Instructor__Name__icontains=search_courses)
        )

        departments = DepartmentInfo.objects.all()

        return render(request, 'courseEnroll/course_search.html', {
            'search_courses': search_courses,
            'courses': courses,
            'action': action,
            'schools': CourseInfo.SCHOOLS,
            'departments': departments,
            'selected_school': school_id,
            'selected_department': department_id,
            'student_info': student_info,
            'remaining_points': remaining_points,  # Add this to context
        })
    else:
        return render(request, 'courseEnroll/course_search.html', {})
    
@login_required
def select_courses(request):
    target_date = timezone.make_aware(datetime(2024, 12, 12, 0, 0, 0))

    def check_time_conflict(student_info, new_course):
        
        enrolled_courses = Enrollment.objects.filter(
            student=student_info, 
            is_waitlisted=False
        )

        conflicts = []
        for enrollment in enrolled_courses:
            existing_course = enrollment.course

            if existing_course.class_days == new_course.class_days:
                existing_start = existing_course.start_time
                existing_end = existing_course.end_time
                new_start = new_course.start_time
                new_end = new_course.end_time

                if not (new_end <= existing_start or new_start >= existing_end):
                    conflicts.append({
                        'existing_course': existing_course.name,
                        'existing_time': f"{existing_course.start_time} - {existing_course.end_time}",
                        'existing_day': existing_course.class_days,
                        'new_course': new_course.name,
                        'new_time': f"{new_course.start_time} - {new_course.end_time}",
                        'new_day': new_course.class_days
                    })

        return conflicts

    if request.method == 'POST':
        student_info = StudentInfo.objects.get(user=request.user)
        
        # Calculate waitlisted points
        waitlist_enrollments = student_info.enrollments.filter(is_waitlisted=True)
        total_waitlist_points = sum(
            float(enrollment.points_assigned or 0)
            for enrollment in waitlist_enrollments
        )
        
        # Calculate remaining points
        remaining_points = 100 - total_waitlist_points

        student_school = student_info.School
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

                if Enrollment.objects.filter(student=student_info, course__name=course.name, is_waitlisted=False).exists():
                    messages.error(request, f"You are already enrolled in a course named '{course.name}'. Please select a different course.")
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
                    # Check for time conflicts before enrollment
                    time_conflicts = check_time_conflict(student_info, course)
                    
                    if time_conflicts:
                        messages.error(request, f"Cannot enroll into this {course.name}, its has time conflicts with your existing courses")
                        continue

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
                    # Validate points before waitlisting
                    if not waitlisted_enrollment:
                        points_assigned = request.POST.get(f'points_{course_id}', 0)
                        try:
                            points_assigned = int(points_assigned)
                            
                            # Point validation checks
                            if points_assigned < 0:
                                messages.error(request, f"Points cannot be negative for {course.name}")
                                continue
                            
                            if points_assigned > remaining_points:
                                messages.error(request,
                                    f"Not enough points available for {course.name}. "
                                    f"Current points: {remaining_points}, "
                                    f"Attempted to assign: {points_assigned}"
                                )
                                continue
                            
                            # Check if course still has capacity for direct enrollment
                            if course.grad_Capacity > 0:
                                messages.error(request, f"{course.name} still has {course.grad_Capacity} slots open, try to enroll instead")
                                continue

                            # Create waitlist enrollment
                            new_enrollment = Enrollment.objects.create(
                                student=student_info, 
                                course=course, 
                                is_waitlisted=True,
                                points_assigned=points_assigned
                            )

                            # Calculate true points based on target date
                            days_difference = max(0, (new_enrollment.created_at - target_date).days)
                            true_points = max(0, points_assigned - (days_difference * 1.6))
                            
                            new_enrollment.true_points = true_points
                            new_enrollment.save()

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

@login_required
def submit_override(request):
    if request.method == 'POST':
        override_form = OverrideFormSubmission(request.POST, user=request.user)
        if override_form.is_valid():
            override_form.save()
            # Add any additional logic here, such as sending a notification email
            return redirect('courseEnroll:dashboard')
    else:
        override_form = OverrideFormSubmission(user=request.user)

    return render(request, 'courseEnroll/dashboard.html', {
        'override_form': override_form,
        # Other context variables
    })

from .models import CourseInfo, Enrollment

@login_required
def submit_prereg(request):
    if request.method == 'POST':
        try:
            student_info = StudentInfo.objects.get(user=request.user)
            
            existing_prereg = PreRegInfo.objects.filter(student_id=student_info).first()
            
            if existing_prereg:
                messages.warning(request, "You have already submitted a pre-registration form.")
                return redirect('courseEnroll:dashboard')
            
            prereg_form = PreRegInfoForm(request.POST, user=request.user)
            
            if prereg_form.is_valid():
                prereg_instance = prereg_form.save(commit=False)
                prereg_instance.student_id = student_info
                prereg_instance.save()
                
                messages.success(request, "Pre-registration submitted successfully!")
            else:
                for field, errors in prereg_form.errors.items():
                    messages.error(request, f"{field}: {', '.join(errors)}")
        
        except StudentInfo.DoesNotExist:
            messages.error(request, "Student profile not found.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
    
    return redirect('courseEnroll:dashboard')