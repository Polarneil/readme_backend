from rest_framework import serializers
from .models import RepoRequest, ReadmeFile


class SuccessSerializer(serializers.Serializer):
    message = serializers.CharField()


class RepoRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepoRequest
        fields = '__all__'


class ReadmeFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadmeFile
        fields = '__all__'
