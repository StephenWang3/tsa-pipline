from django.urls import path
from .views import process_file, test, get_result

urlpatterns = [
    path('process/', process_file, name='process_file'),
    path('test/', test, name='test'),
    path('getResult/', get_result, name='getResult')
]