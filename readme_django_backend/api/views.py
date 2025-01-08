from rest_framework.response import Response
from rest_framework import generics, status
from .serializers import SuccessSerializer, RepoRequestSerializer


class TestEndpoint(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        data = {"message": "Success"}
        serializer = SuccessSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class RepoRequestView(generics.ListCreateAPIView):
    serializer_class = RepoRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = RepoRequestSerializer(data=request.data)

        if serializer.is_valid():
            repo_request_obj = serializer.save()  # Save the message to db
            print(f"Repo Request Created: {repo_request_obj}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
