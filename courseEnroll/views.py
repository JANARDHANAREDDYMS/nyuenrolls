from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from userprofile.models import StudentInfo
from .models import CourseInfo
from django.db.models import Q



@login_required
def dashboard(request):
    student_info = StudentInfo.objects.get(user=request.user)
    enrolled_courses = student_info.course_enrolled.all()
    

    return render(request, 'courseEnroll/dashboard.html', {
        'student_info': student_info,
        'enrolled_courses': enrolled_courses,
    })

def search_courses(request):
    if request.method == 'POST':
        search_courses = request.POST.get('search_courses','')
        courses = CourseInfo.objects.filter(
            Q(course_id__icontains=search_courses) |
            Q(name__icontains=search_courses) | 
            Q(description__icontains=search_courses) |  
            Q(Instructor__Name__icontains=search_courses)  
        )
        return render(request,'courseEnroll/course_search.html',{'search_courses':search_courses,
                                                                 'courses':courses})
    else:
        return render(request,'courseEnroll/course_search.html',{})
    
def select_courses(request):
    if request.method == 'POST':
        selected_courses = request.POST.getlist('selected_courses')
        
        for course_id in selected_courses:
            course = CourseInfo.objects.get(course_id=course_id)
            request.user.studentinfo.course_enrolled.add(course)

        return redirect('courseEnroll:dashboard')