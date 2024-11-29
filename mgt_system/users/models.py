# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('Administrator', 'Administrator'),
        ('Manager', 'Manager'),
        ('Employee', 'Employee'),
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Employee')

class Document(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()

    class Meta:
        permissions = [
            ("custom_add_document", "Can custom add document"),
            ("custom_view_document", "Can custom view document"),
        ]
