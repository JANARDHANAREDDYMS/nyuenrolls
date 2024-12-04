from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from userprofile.models import DepartmentInfo,FacultyInfo,StudentInfo
from django.http import HttpResponse
from courseEnroll.models import CourseInfo, OverrideForm, PreRegInfo
from datetime import date,datetime
from django.contrib import messages
from courseEnroll.forms import OverrideFormSubmission
from django.db.models import Q


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
        #instructor_name = request.POST.get('instructor')
        capacity = request.POST.get('capacity')
        phd_seats = request.POST.get('phdSeats')
        class_day = request.POST.get('classDay')
        class_time = request.POST.get('classTime')
        course_description = request.POST.get('courseDescription')
        credits = request.POST.get('credits')

        try:
            department = DepartmentInfo.objects.get(department_id=department_code)
            #instructor = FacultyInfo.objects.create(facName=instructor_name)
            CourseInfo.objects.create(
                course_id=course_id,
                name=course_name,
                Department=department,
                #Instructor=instructor,
                course_Capacity=capacity,
                phd_course_capacity=phd_seats,
                class_day=date.today(),
                class_time=datetime.now().time(),
                description=course_description,
                to_waitlist=False,
                credits=credits,
            )
            messages.success(request, "Course has been added successfully!")
        except Exception as e:
            messages.error(request, "Course could not be added: " + str(e))

        return redirect('systemadmin:dashboard')

    return HttpResponse("Invalid Request", status=400)

def course_update(request):
    if request.method == 'POST':
        course_id = request.POST.get('courseId')
        course_name = request.POST.get('courseName')
        department_code = request.POST.get('department')
        #instructor_name = request.POST.get('instructor')
        capacity = request.POST.get('capacity')
        phd_seats = request.POST.get('phdSeats')
        class_day = request.POST.get('classDay')
        class_time = request.POST.get('classTime')
        course_description = request.POST.get('courseDescription')
        credits = request.POST.get('credits')

        # Retrieve the course to update
        course = get_object_or_404(CourseInfo, course_id=course_id)

        try:
            if CourseInfo.objects.filter(course_id=new_course_id).exists():
                messages.error(request, "Course ID already exists. Please choose a different one.")
                return redirect('systemadmin:dashboard')

            # Update the course attributes
            course.course_id = course_id  # Change the course_id

            course.name = course_name
            course.Department = get_object_or_404(DepartmentInfo, department_id=department_code)
            #course.Instructor=instructor,
            course.course_Capacity = capacity
            course.phd_course_capacity = phd_seats
            course.class_day = date.today(),  # Make sure to convert if necessary
            course.class_time = datetime.now().time()  # Make sure to convert if necessary
            course.description = course_description
            course.credits = credits
            
            # Save the updated course information
            course.save()

            messages.success(request, "Course has been updated successfully!")
        except Exception as e:
            messages.error(request, "Course could not be updated: " + str(e))

        return redirect('systemadmin:dashboard')

    return HttpResponse("Invalid Request", status=400)

def course_delete(request):
    if request.method == 'POST':
        course_id = request.POST.get('courseId')
        
        # Get the course object, or return a 404 if not found
        course = get_object_or_404(CourseInfo, course_id=course_id)

        try:
            # Delete the course
            course.delete()
            messages.success(request, "Course has been deleted successfully!")
        except Exception as e:
            messages.error(request, "Course could not be deleted: " + str(e))

        return redirect('systemadmin:dashboard')

    return HttpResponse("Invalid Request", status=400)