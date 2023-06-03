from django.shortcuts import render
from django.contrib.auth.decorators import login_required


# @login_required  # Requires user authentication
def result_home(request):
    if request.user.role == 'teacher':
        template_name = 'result_home.html'
    elif request.user.role == 'student':
        template_name = 'result_student.html'
    else:
        # Handle other roles or scenarios, if needed
        template_name = 'default.html'

    return render(request, template_name)
