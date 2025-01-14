import os
import tempfile
import git
import openai
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.mixins import UpdateModelMixin
from django.shortcuts import get_object_or_404
from dotenv import load_dotenv

from .models import RepoRequest, ReadMeFile
from .serializers import SuccessSerializer, RepoRequestSerializer, ReadmeFileSerializer

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai.api_key)


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
            repo_request_obj = serializer.save()
            print(f"Repo Request Created: {repo_request_obj}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        queryset = RepoRequest.objects.all()
        return queryset


class ReadMeFileView(generics.ListCreateAPIView, UpdateModelMixin):
    serializer_class = ReadmeFileSerializer

    def clone_repo(self, repo_url):
        temp_dir = tempfile.mkdtemp()
        git.Repo.clone_from(repo_url, temp_dir)
        return temp_dir

    def analyze_repo(self, repo_path):
        repo_summary = {}
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if file.endswith((
                        '.c', '.cpp', '.cs', '.java', '.py', '.js', '.ts', '.jsx', '.tsx',
                        '.rb', '.php', '.swift', '.go', '.rs', '.kt', '.m', '.r', '.pl',
                        '.lua', '.sh', '.html', '.css', '.scss', '.xml', '.json', '.yml',
                        '.yaml', '.sql', 'Dockerfile', '.ipynb', '.csv', '.txt'
                )):
                    with open(os.path.join(root, file), 'r') as f:
                        repo_summary[file] = f.read()[:1000]  # Limit to first 1000 chars
        return repo_summary

    def generate_prompt(self, request, repo_summary):
        repo_request_id = request.data.get('repo_request')
        repo_request = get_object_or_404(RepoRequest, id=repo_request_id)
        repo_url = repo_request.repo_url

        example_format = "# Project Name..."
        non_example_format = "```markdown # Project Name...```"

        prompt = f"Generate a professional README.md for the following code repository. This is the git url, make sure to include it in the instructions if you add lines like git clone <repo url>: {repo_url}\n\n"
        for file, content in repo_summary.items():
            prompt += f"File: {file}\nContent:\n{content}\n\n"
        prompt += "Provide a project overview, installation instructions, usage, and contribution guidelines."
        prompt += f"Do not include ```markdown backticks in your response. Just write the response in markdown. Use this example for reference: {example_format}. Not like this: {non_example_format}"
        return prompt

    def generate_readme(self, prompt):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        return response.choices[0].message.content

    def create(self, request, *args, **kwargs):
        repo_request_id = request.data.get('repo_request')

        repo_request = get_object_or_404(RepoRequest, id=repo_request_id)

        readme_file, created = ReadMeFile.objects.get_or_create(
            repo_request=repo_request,
            defaults={'content': ''}
        )

        if not created:
            return Response(
                {"detail": f"README for {repo_request.repo_url} already exists.", "readme_id": readme_file.id},
                status=status.HTTP_200_OK
            )

        try:
            # Clone and analyze the repository
            repo_path = self.clone_repo(repo_request.repo_url)
            repo_summary = self.analyze_repo(repo_path)

            # Generate README content using AI
            prompt = self.generate_prompt(request, repo_summary)
            readme_content = self.generate_readme(prompt)

            # Save content to model and clean up
            readme_file.content = readme_content
            readme_file.save()

            # Remove temp directory
            os.system(f"rm -rf {repo_path}")

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = self.get_serializer(readme_file)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        key = request.GET.get('key')
        if not key:
            return Response({'error': 'Key parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            readme_file = ReadMeFile.objects.get(key=key)
            serializer = ReadmeFileSerializer(readme_file)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ReadMeFile.DoesNotExist:
            return Response({'error': 'ReadMeFile with this key does not exist.'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, *args, **kwargs):
        key = request.data.get('key')
        new_content = request.data.get('content')

        if not key or new_content is None:
            return Response({'error': 'Key and content are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            readme_file = ReadMeFile.objects.get(key=key)
            readme_file.content = new_content
            readme_file.save()

            serializer = self.get_serializer(readme_file)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ReadMeFile.DoesNotExist:
            return Response({'error': 'ReadMeFile with this key does not exist.'}, status=status.HTTP_404_NOT_FOUND)
