# documents/models.py

from django.conf import settings
from django.db import models

class Workflow(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name



from django.utils import timezone

class Document(models.Model):
    DOCUMENT_TYPES = [
        ('Invoice', 'Invoice'),
        ('Contract', 'Contract'),
        ('Report', 'Report'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    title = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=DOCUMENT_TYPES, default='Invoice')
    content = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE , null=True)
    created_at = models.DateTimeField(default=timezone.now)
    workflows = models.ManyToManyField('Workflow', related_name='documents')

    def __str__(self):
        return self.title

