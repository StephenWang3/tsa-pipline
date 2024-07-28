from django.urls import path
from .views import process_file, test

urlpatterns = [
    path('process/', process_file, name='process_file'),
    path('test/', test, name='test'),
]