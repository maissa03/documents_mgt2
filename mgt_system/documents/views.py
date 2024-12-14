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
from .models import Workflow, Document, WorkflowStage, WorkflowInstance, StageTransition
from .serializers import (WorkflowSerializer, DocumentSerializer,WorkflowStageSerializer, WorkflowInstanceSerializer,StageTransitionSerializer)


class WorkflowViewSet(viewsets.ModelViewSet):
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer


class WorkflowStageViewSet(viewsets.ModelViewSet):
    queryset = WorkflowStage.objects.all()
    serializer_class = WorkflowStageSerializer


class WorkflowInstanceViewSet(viewsets.ModelViewSet):
    queryset = WorkflowInstance.objects.all()
    serializer_class = WorkflowInstanceSerializer


class StageTransitionViewSet(viewsets.ModelViewSet):
    queryset = StageTransition.objects.all()
    serializer_class = StageTransitionSerializer




from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from transformers import pipeline
import PyPDF2

from .models import Document, Workflow
from .serializers import DocumentSerializer, WorkflowSerializer
from stable_baselines3 import PPO
from django.shortcuts import get_object_or_404
from .management.commands.workflow_env import WorkflowEnvironment

# Initialize the HuggingFace pipelines
classifier = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')
summarizer = pipeline('summarization', model='sshleifer/distilbart-cnn-12-6')


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Handles file upload, text extraction, summarization, classification, and workflow assignment."""
        # Check if the file is uploaded
        file = self.request.FILES.get('file_path')
        if not file:
            raise ValidationError("A file must be uploaded.")

        # Extract text from the PDF file
        pdf_reader = PyPDF2.PdfReader(file)
        document_content = ""
        for page in pdf_reader.pages:
            document_content += page.extract_text() or ""
        print("Extracted Content:", document_content)

        # Summarize the content using HuggingFace pipeline
        summarized_content = summarizer(document_content, max_length=1000000, min_length=5, do_sample=False)
        summary_text = summarized_content[0]['summary_text']

        # Classify the summarized content
        result = classifier(document_content, candidate_labels=['Invoice', 'Contract', 'Report'])
        document_type = result['labels'][0]  # Get the most likely label

        # Save the document with extracted details
        document = serializer.save(
            uploaded_by=self.request.user,
            content=summary_text,
            type=document_type,
        )

        # After saving the document, assign the workflow manager
        self.assign_workflow_manager(document, document_type)

    def assign_workflow_manager(self, document, document_type):
        """Assign the workflow manager based on the RL model."""
        try:
            model = PPO.load("workflow_rl_model")
        except FileNotFoundError:
            raise ValidationError("Trained RL model not found. Please train the model first.")

        # Get the appropriate workflow based on document type
        workflow = self._get_workflow_based_on_document_type(document_type)

        env = WorkflowEnvironment()
        current_state = env.reset()
        action, _ = model.predict(current_state, deterministic=True)

        try:
            selected_manager = env.managers[int(action)]
        except IndexError:
            raise ValidationError(f"Invalid action: {action}. Please check the RL model and environment setup.")

        # Assign workflow to the selected manager
        workflow_instance = WorkflowInstance.objects.create(
            workflow=workflow,
            document=document,
            performed_by=selected_manager,
            status="In Progress"
        )

        # Associate the workflow instance with the document
        document.workflow_instance = workflow_instance
        document.save()

        print(f"Workflow '{workflow.name}' assigned to manager '{selected_manager.username}'.")

    def _get_workflow_based_on_document_type(self, document_type):
        """Logic to get the appropriate workflow based on document type."""
        try:
            if document_type == "Report":
                return Workflow.objects.get(name="Report")  # Corrected to match the name in the database
            elif document_type == "Invoice":
                return Workflow.objects.get(name="invoice")  # Corrected to match the name in the database
            else:
                raise ValidationError(f"Unknown document type: {document_type}")
        except Workflow.DoesNotExist:
            raise ValidationError(f"Workflow for '{document_type}' not found. Please create the appropriate workflow in the system.")

    def get_queryset(self):
        """Filter documents by user role."""
        user = self.request.user
        queryset = Document.objects.all()
        if user.groups.filter(name="Employees").exists():
            queryset = queryset.filter(uploaded_by=user)
        return queryset


'''
    
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from stable_baselines3 import PPO
from .models import Workflow, WorkflowInstance, User
from .management.commands.workflow_env import WorkflowEnvironment

class AssignWorkflowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, workflow_id):
        # Load the trained RL model
        try:
            model = PPO.load("workflow_rl_model")
        except FileNotFoundError:
            raise ValidationError("Trained RL model not found. Please train the model first.")

        # Get the workflow to be assigned
        workflow = get_object_or_404(Workflow, id=workflow_id)

        # Initialize the environment
        env = WorkflowEnvironment()

        # Reset the environment to get the initial state
        current_state = env.reset()

        # Predict the best action (manager assignment) using the RL model
        action, _ = model.predict(current_state, deterministic=True)

        # Assign the workflow to the selected manager
        try:
            selected_manager = env.managers[action]
        except IndexError:
            raise ValidationError(f"Invalid action: {action}. Please check the RL model and environment setup.")

        # Create a WorkflowInstance
        WorkflowInstance.objects.create(
            workflow=workflow,
            performed_by=selected_manager,
            status="Assigned"
        )

        return Response({
            "message": f"Workflow '{workflow.name}' assigned to manager '{selected_manager.username}'.",
            "manager_id": selected_manager.id,
            "workflow_id": workflow.id
        })

        '''

########################################################################################

'''
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
