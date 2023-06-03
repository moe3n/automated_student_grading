from django.shortcuts import render
from django.http import HttpResponse


def course_list(request):
    return render(request, 'courses/course_list.html')


def course_details(request):
    return render(request, 'courses/course_details.html')


def new_exam(request):
    return render(request, 'courses/new_exam.html')
