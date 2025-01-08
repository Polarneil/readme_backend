from django.urls import path
from .views import TestEndpoint, RepoRequestView, ReadMeFileView

urlpatterns = [
    path('test/', TestEndpoint.as_view(), name='test'),
    path('repo/', RepoRequestView.as_view(), name='repo'),
    path('trigger-readme/', ReadMeFileView.as_view(), name='readme')
]
