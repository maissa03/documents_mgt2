'''from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Document, Workflow
from .serializers import DocumentSerializer, WorkflowSerializer



class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

class WorkflowViewSet(viewsets.ModelViewSet):
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer'''



from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from transformers import pipeline
import PyPDF2

from .models import Document, Workflow
from .serializers import DocumentSerializer, WorkflowSerializer

# Initialize the HuggingFace pipelines
classifier = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')
summarizer = pipeline('summarization', model='sshleifer/distilbart-cnn-12-6')


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Handles file upload, text extraction, summarization, and classification."""
        # Check if the file is uploaded
        file = self.request.FILES.get('file')
        if not file:
            raise ValidationError("A file must be uploaded.")

        # Extract text from the PDF file
        pdf_reader = PyPDF2.PdfReader(file)
        document_content = ""
        for page in pdf_reader.pages:
            document_content += page.extract_text() or ""
        print("Extracted Content:", document_content)

        # Summarize the content using HuggingFace pipeline
        summarized_content = summarizer(document_content, max_length=10000, min_length=5, do_sample=False)
        summary_text = summarized_content[0]['summary_text']

        # Classify the summarized content
        result = classifier(summary_text, candidate_labels=['Invoice', 'Contract', 'Report'])
        document_type = result['labels'][0]  # Get the most likely label

        # Save the document with extracted details
        serializer.save(
            uploaded_by=self.request.user,
            content=summary_text,
            type=document_type,
        )

    def get_queryset(self):
        """Filter documents by user role."""
        user = self.request.user
        queryset = Document.objects.all()
        if user.groups.filter(name="Employees").exists():
            queryset = queryset.filter(uploaded_by=user)
        return queryset


class WorkflowViewSet(viewsets.ModelViewSet):
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='assign-workflow')
    def assign_to_workflow(self, request, pk=None):
        """Assigns a document to a specified workflow."""
        document = self.get_object()
        workflow_id = request.data.get('workflow_id')

        try:
            workflow = Workflow.objects.get(id=workflow_id)
            document.workflows.add(workflow)
            document.save()
            return Response({'message': f'Document {document.title} assigned to workflow {workflow.name}.'})
        except Workflow.DoesNotExist:
            return Response({'error': 'Workflow not found.'}, status=404)



'''
class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    @action(detail=True, methods=['post'])
    def summarize(self, request, pk=None):
        document = self.get_object()
        summary = document.summarize()
        return Response({'summary': summary})

    @action(detail=True, methods=['post'])
    def classify(self, request, pk=None):
        document = self.get_object()
        classification = document.classify()
        return Response({'classification': classification})


class WorkflowViewSet(viewsets.ModelViewSet):
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer'''
