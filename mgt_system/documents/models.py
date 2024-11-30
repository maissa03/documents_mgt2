from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from transformers import pipeline  # For summarization and classification (Hugging Face Transformers)
import logging

# Configure file storage
fs = FileSystemStorage(location='uploads/')  # Change path as needed

logger = logging.getLogger(__name__)

class Workflow(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name


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
    uploaded_file = models.FileField(storage=fs, upload_to='documents/', null=True, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    workflows = models.ManyToManyField('Workflow', related_name='documents')

    def __str__(self):
        return self.title

    def summarize(self):
        """
        Generate a summary of the document content.
        """
        try:
            summarizer = pipeline("summarization")
            summary = summarizer(self.content, max_length=50, min_length=10, do_sample=False)
            return summary[0]['summary_text']
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return "Summarization not available."

    def assign_document_to_workflow(self, workflow):
        """
        Assign the document to a workflow.
        """
        try:
            self.workflows.add(workflow)
            self.save()
            return f"Document assigned to workflow: {workflow.name}"
        except Exception as e:
            logger.error(f"Failed to assign document to workflow: {e}")
            return "Assignment failed."

    def classify(self):
        """
        Classify the document into one of the predefined types using AI.
        """
        try:
            classifier = pipeline("zero-shot-classification")
            candidate_labels = [choice[0] for choice in self.DOCUMENT_TYPES]
            result = classifier(self.content, candidate_labels)
            self.type = result['labels'][0]  
            self.save()
            return f"Document classified as: {self.type}"
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return "Classification not available."
