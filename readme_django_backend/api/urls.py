from django.urls import path
from .views import RepoRequestList

urlpatterns = [
    path('test/', RepoRequestList.as_view(), name='test')
]
