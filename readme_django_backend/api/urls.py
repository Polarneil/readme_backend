from django.urls import path
from .views import TestEndpoint, RepoRequestView

urlpatterns = [
    path('test/', TestEndpoint.as_view(), name='test'),
    path('repo/', RepoRequestView.as_view(), name='repo')
]
