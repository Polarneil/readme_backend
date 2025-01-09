from django.db import models


class RepoRequest(models.Model):
    repo_url = models.URLField(unique=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)


class ReadMeFile(models.Model):
    repo_request = models.OneToOneField(
        RepoRequest,
        on_delete=models.CASCADE,
        related_name='readme'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
