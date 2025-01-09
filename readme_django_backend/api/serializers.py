from rest_framework import serializers
from .models import RepoRequest, ReadMeFile


class SuccessSerializer(serializers.Serializer):
    message = serializers.CharField()


class RepoRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepoRequest
        fields = '__all__'


class ReadmeFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadMeFile
        fields = '__all__'
