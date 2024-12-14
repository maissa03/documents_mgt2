'''from django.conf import settings
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
            '''


from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage

class Workflow(models.Model): 
    name = models.CharField(max_length=255) 
    description = models.CharField(max_length=255, default="Default description")
    created_by = models.ForeignKey(User, related_name='created_workflows', on_delete=models.SET_NULL, null=True) 
    def __str__(self): return self.name



class Document(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Submitted', 'Submitted'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ]
    
    TYPE_CHOICES = [
        ('Invoice', 'Invoice'),
        ('Report', 'Report'),
        ('Contract', 'Contract')
    ]
    
    uploaded_by = models.ForeignKey(
        User, related_name='uploaded_documents', on_delete=models.SET_NULL, null=True, blank=True
    )
    content = models.TextField(default='waiting for IA')
    title = models.CharField(max_length=255)
    file_path = models.FileField(upload_to='documents/', default='default/path/to/file.txt')
    status = models.CharField(choices=STATUS_CHOICES, max_length=10)
    type = models.CharField(choices=TYPE_CHOICES, max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title



class WorkflowStage(models.Model):
    workflow = models.ForeignKey(Workflow, related_name='stages', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    stage_order = models.IntegerField()
    action_required = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.workflow.name} - {self.name}'




class WorkflowInstance(models.Model):
    STATUS_CHOICES = [
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed')
    ]

    document = models.OneToOneField(
    Document, related_name='workflow_instance', on_delete=models.CASCADE, null=True, blank=True)
    
    workflow = models.ForeignKey(
        Workflow, related_name='instances', on_delete=models.CASCADE
    )
    current_stage = models.ForeignKey(
        WorkflowStage, related_name='current_instances', on_delete=models.CASCADE, null=True, blank=True
    )
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default='In Progress')
    created_at = models.DateTimeField(auto_now_add=True)
    performed_by = models.ForeignKey(
        User, related_name='performed_transitions', on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        return f'Workflow for {self.document.title} - {self.status}'





class StageTransition(models.Model):
    workflow_instance = models.ForeignKey(
        WorkflowInstance, related_name='transitions', on_delete=models.CASCADE
    )
    from_stage = models.ForeignKey(
        WorkflowStage, related_name='from_transitions', on_delete=models.CASCADE
    )
    to_stage = models.ForeignKey(
        WorkflowStage, related_name='to_transitions', on_delete=models.CASCADE
    )
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'WorkflowInstance {self.workflow_instance.id} - {self.from_stage.name} to {self.to_stage.name}'




'''
from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage

class Workflow(models.Model):
    STEP_CHOICES = [
        ('Pending', 'Pending'),
        ('Under Review', 'Under Review'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    
    step = models.CharField(max_length=50, choices=STEP_CHOICES,null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Step: {self.step} - {self.name}"
    
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
        ('Modification Requested', 'Modification Requested'),
    ]
    
    title = models.CharField(max_length=255)
    content = models.TextField()
    type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    workflows = models.ManyToManyField('Workflow', null=True, blank=True, related_name='documents')

    file = models.FileField(upload_to='documents/', null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
fs = FileSystemStorage(location='uploads/')  # Change path as needed
'''