from django.urls import path
from .views import generate_excel, template_view

urlpatterns = [
    path('template/', template_view, name='template_view'),
    path('generate-excel/', generate_excel, name='generate_excel'),
]
