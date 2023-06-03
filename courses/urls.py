from django.urls import path
from . import views

app_name = 'courses'
urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('details/', views.course_details, name='course_details'),
    path('details/new_exam/', views.new_exam, name='new_exam'),
]
