from rest_framework.response import Response
from rest_framework import generics, status
from django.shortcuts import get_object_or_404

from .models import RepoRequest, ReadmeFile
from .serializers import SuccessSerializer, RepoRequestSerializer, ReadmeFileSerializer


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

    def get_queryset(self):
        queryset = RepoRequest.objects.all()
        return queryset


class ReadMeFileView(generics.ListCreateAPIView):
    serializer_class = ReadmeFileSerializer

    def create(self, request, *args, **kwargs):
        # Extract the repo_request ID from the incoming request
        repo_request_id = request.data.get('repo_request')

        # Ensure the associated RepoRequest exists
        repo_request = get_object_or_404(RepoRequest, id=repo_request_id)

        # Check if a ReadmeFile already exists for this RepoRequest
        readme_file, created = ReadmeFile.objects.get_or_create(
            repo_request=repo_request,
            defaults={'content': ''}
        )

        if not created:
            # If the ReadmeFile already exists, return its data
            return Response(
                {"detail": "Readme already exists.", "readme_id": readme_file.id},
                status=status.HTTP_200_OK
            )

        # AI Logic Placeholder: Generate README content
        # This is where the AI-based README generation will happen.
        # For now, using a static placeholder.
        readme_file.content = f"# README for {repo_request.repo_url}\n\nGenerated content goes here."
        readme_file.save()

        # Serialize the created/updated object
        serializer = self.get_serializer(readme_file)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        # Return all ReadmeFile objects
        queryset = ReadmeFile.objects.all()
        return queryset
