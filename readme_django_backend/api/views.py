from rest_framework import generics
from rest_framework.response import Response
from .serializers import SuccessSerializer


class RepoRequestList(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        data = {"message": "Success"}
        serializer = SuccessSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
