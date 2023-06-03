from django.urls import path
from . import views

urlpatterns = [
    path('', views.result_home, name='result_home'),

]
