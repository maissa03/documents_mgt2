from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from transformers import pipeline
import PyPDF2

from .models import Workflow, Document, WorkflowStage, WorkflowInstance, StageTransition,User
from .serializers import (
    WorkflowSerializer, DocumentSerializer,
    WorkflowStageSerializer, WorkflowInstanceSerializer,
    StageTransitionSerializer
)
from stable_baselines3 import PPO
from django.shortcuts import get_object_or_404
from .management.commands.workflow_env import WorkflowEnvironment
import requests
from requests.auth import HTTPBasicAuth

# Initialize HuggingFace pipelines
classifier = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')
summarizer = pipeline('summarization', model='sshleifer/distilbart-cnn-12-6')

# -------------------------
# Workflow Management Viewsets
# -------------------------


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
import requests
from requests.auth import HTTPBasicAuth

# Initialize the HuggingFace pipelines
classifier = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')
summarizer = pipeline('summarization', model='sshleifer/distilbart-cnn-12-6')


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Handles document creation with file upload, text extraction, summarization, and workflow assignment."""
        # Check if a file was uploaded
        file = self.request.FILES.get('file_path')
        if not file:
            raise ValidationError("A file must be uploaded.")

        # Extract text from PDF
        pdf_reader = PyPDF2.PdfReader(file)
        document_content = ""
        for page in pdf_reader.pages:
            document_content += page.extract_text() or ""
        print("Extracted Content:", document_content)

        # Summarize the document content
        summarized_content = summarizer(document_content, max_length=150, min_length=5, do_sample=False)
        summary_text = summarized_content[0]['summary_text']

        # Classify document type
        result = classifier(document_content, candidate_labels=['Invoice', 'Contract', 'Report'])
        document_type = result['labels'][0]  # Most probable label

        # Save the document instance
        document = serializer.save(
            uploaded_by=self.request.user,
            content=summary_text,
            type=document_type,
        )

        ################################################################################################################################
        # Synchronize with Nextcloud
        try:
            self.synchronize_with_nextcloud(file, document)
        except Exception as e:
            print(f"Nextcloud synchronization error: {str(e)}")
            document.synced_to_nextcloud = False
            document.save()

        ################################################################################################################################

        # Assign workflow and manager using RL
        self.assign_workflow_manager(document, document_type)
    
    def synchronize_with_nextcloud(self, file, document_instance):
        """Uploads the document to Nextcloud."""
        # Nextcloud credentials and upload URL
        NEXTCLOUD_URL = "https://use08.thegood.cloud/remote.php/dav/files"
        NEXTCLOUD_USERNAME = "maalejmaissa7@gmail.com"
        NEXTCLOUD_PASSWORD = "Qb#M5!Xz@A@kX.f"
        NEXTCLOUD_UPLOAD_DIR = f"{NEXTCLOUD_URL}/{NEXTCLOUD_USERNAME}/uploaded_documents"

        # Step 1: Ensure the Nextcloud folder exists
        folder_path = f"{NEXTCLOUD_UPLOAD_DIR}"
        response = requests.request(
            "MKCOL",
            folder_path,
            auth=HTTPBasicAuth(NEXTCLOUD_USERNAME, NEXTCLOUD_PASSWORD)
        )

        # MKCOL responses: 201 = Created, 405 = Already Exists
        if response.status_code not in [201, 405]:
            raise Exception(f"Failed to create Nextcloud folder: {response.status_code}, {response.text}")

        # Step 2: Upload the file
        file_path = f"{NEXTCLOUD_UPLOAD_DIR}/{file.name}"

        # Ensure the file content is read correctly
        file.seek(0)
        file_content = file.read()

        upload_response = requests.put(
            file_path,
            data=file_content,
            auth=HTTPBasicAuth(NEXTCLOUD_USERNAME, NEXTCLOUD_PASSWORD)
        )

        if upload_response.status_code in [201, 204]:  # 201 = Created, 204 = Updated
            upload_url = file_path
            print(f"File successfully uploaded to Nextcloud: {upload_url}")
            document_instance.synced_to_nextcloud = True
            document_instance.nextcloud_url = upload_url  # Store Nextcloud URL in the model
            document_instance.save()
        else:
            raise Exception(f"Nextcloud upload failed: {upload_response.status_code}, {upload_response.text}")

    def assign_workflow_manager(self, document, document_type):
        """Assign a workflow manager using the RL model and environment."""
        try:
            model = PPO.load("workflow_rl_model")
        except FileNotFoundError:
            raise ValidationError("Trained RL model not found. Please train the model first.")

        # Get the appropriate workflow based on document type
        workflow = self._get_workflow_based_on_document_type(document_type)

        # Use RL environment to select the best manager
        env = WorkflowEnvironment()
        current_state = env.reset()
        action, _ = model.predict(current_state, deterministic=True)

        # Clip the action to be within valid range
        num_managers = len(env.managers)
        action = min(action, num_managers - 1)  # Clip the action if it exceeds the available managers
        print(action)
        try:
            selected_manager = env.managers[action-1]
        except IndexError:
            raise ValidationError(f"Invalid action: {action}. Check RL model predictions and environment setup.")

        # Create a workflow instance for the selected manager
        workflow_instance = WorkflowInstance.objects.create(
            workflow=workflow,
            document=document,
            performed_by=selected_manager,
            current_stage="Review Document",
            status="In Progress"
        )

        document.workflow_instance = workflow_instance
        document.save()

        print(f"Workflow '{workflow.name}' assigned to manager '{selected_manager.username}'.")


    def _get_workflow_based_on_document_type(self, document_type):
        """Return the workflow object based on document type."""
        try:
            if document_type == "Report":
                return Workflow.objects.get(name="Report")
            elif document_type == "Invoice":
                return Workflow.objects.get(name="invoice")
            elif document_type == "Contract":
                return Workflow.objects.get(name="Contract")
            else:
                raise ValidationError(f"Unknown document type: {document_type}")
        except Workflow.DoesNotExist:
            raise ValidationError(f"Workflow for '{document_type}' not found. Create the workflow in the system.")
    def get_queryset(self):
        """Filter documents by user role."""
        user = self.request.user
        queryset = Document.objects.all()
        if user.groups.filter(name="Employees").exists():
            queryset = queryset.filter(uploaded_by=user)
        return queryset
    

############################################################################################################################################################
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import MultiPartParser
import base64
from django.http import JsonResponse
NEXTCLOUD_URL = "https://use08.thegood.cloud/remote.php/dav/files"
NEXTCLOUD_USERNAME = "maalejmaissa7@gmail.com"
NEXTCLOUD_PASSWORD = "Qb#M5!Xz@A@kX.f"
from rest_framework.exceptions import ValidationError
import base64
import io
import PyPDF2

classifier = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')
summarizer = pipeline('summarization', model='sshleifer/distilbart-cnn-12-6')

class HandleSOAPDocumentView(APIView):
    permission_classes = [AllowAny]

    # Constants for REST authentication
    REST_API_USERNAME = "missou"
    REST_API_PASSWORD = "admin"

    def post(self, request):
        """Handle incoming SOAP document."""
        # 1. Verify Authorization Header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Basic '):
            return Response({'error': 'Unauthorized'}, status=401)

        credentials = base64.b64decode(auth_header.split(' ')[1]).decode('utf-8')
        username, password = credentials.split(':')
        if username != self.REST_API_USERNAME or password != self.REST_API_PASSWORD:
            return Response({'error': 'Unauthorized'}, status=401)

        # 2. Extract Data
        document_name = request.data.get("document_name")
        content = request.data.get("content")  # Base64-encoded content

        if not document_name or not content:
            return Response({'error': 'Missing document_name or content'}, status=400)

        # 3. Decode File Content
        try:
            file_content = base64.b64decode(content)
            pdf_file = io.BytesIO(file_content)
        except Exception as e:
            return Response({'error': f"Invalid content encoding: {str(e)}"}, status=400)

        # 4. Extract and Summarize Text
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        extracted_text = "".join(page.extract_text() or "" for page in pdf_reader.pages)

        summarized_content = summarizer(extracted_text, max_length=150, min_length=5, do_sample=False)
        summary_text = summarized_content[0]['summary_text']

        # 5. Classify Document Type
        result = classifier(extracted_text, candidate_labels=['Invoice', 'Contract', 'Report'])
        document_type = result['labels'][0]
        print(User.objects.get(id=1),document_name,content,document_type)
        # 6. Save Document in Database
        
        document = Document.objects.create(
                uploaded_by = User.objects.get(id=1),  # Assuming admin user ID is 1
                file_path=document_name,
                content=summary_text,
                type=document_type
            )
        document.save()
        print(f"Document saved: {document.id}")
        ################################################################################################################################
        # Synchronize with Nextcloud
        try:
            self.synchronize_with_nextcloud(pdf_file, document)
        except Exception as e:
            print(f"Nextcloud synchronization error: {str(e)}")
            document.synced_to_nextcloud = False
            document.save()

        ################################################################################################################################

        # 7. Assign Workflow and Manager
        self.assign_workflow_manager(document, document_type)

        return Response({"message": f"Document '{document_name}' successfully handled and assigned."}, status=201)
    
    def synchronize_with_nextcloud(self, file, document_instance):
        """Uploads the document to Nextcloud."""
        # Nextcloud credentials and upload URL
        NEXTCLOUD_URL = "https://use08.thegood.cloud/remote.php/dav/files"
        NEXTCLOUD_USERNAME = "maalejmaissa7@gmail.com"
        NEXTCLOUD_PASSWORD = "Qb#M5!Xz@A@kX.f"
        NEXTCLOUD_UPLOAD_DIR = f"{NEXTCLOUD_URL}/{NEXTCLOUD_USERNAME}/uploaded_documents"

        # Step 1: Ensure the Nextcloud folder exists
        folder_path = f"{NEXTCLOUD_UPLOAD_DIR}"
        response = requests.request(
            "MKCOL",
            folder_path,
            auth=HTTPBasicAuth(NEXTCLOUD_USERNAME, NEXTCLOUD_PASSWORD)
        )

        # MKCOL responses: 201 = Created, 405 = Already Exists
        if response.status_code not in [201, 405]:
            raise Exception(f"Failed to create Nextcloud folder: {response.status_code}, {response.text}")

        # Step 2: Upload the file
        file_name = document_instance.file_path  # Use the document_name from the database
        file_path = f"{NEXTCLOUD_UPLOAD_DIR}/{file_name}"

        # Ensure the file pointer is reset and read the content
        file.seek(0)  # Reset file pointer
        file_content = file.read()

        upload_response = requests.put(
            file_path,
            data=file_content,
            auth=HTTPBasicAuth(NEXTCLOUD_USERNAME, NEXTCLOUD_PASSWORD)
        )

        # Step 3: Handle upload response
        if upload_response.status_code in [201, 204]:  # 201 = Created, 204 = Updated
            upload_url = file_path
            print(f"File successfully uploaded to Nextcloud: {upload_url}")
            document_instance.synced_to_nextcloud = True
            document_instance.nextcloud_url = upload_url  # Store Nextcloud URL in the model
            document_instance.save()
        else:
            raise Exception(f"Nextcloud upload failed: {upload_response.status_code}, {upload_response.text}")


    def assign_workflow_manager(self, document, document_type):
        """Assign a workflow manager using RL (Reinforcement Learning)."""
        try:
            model = PPO.load("workflow_rl_model")
        except FileNotFoundError:
            raise ValidationError("Trained RL model not found. Please train the model first.")

        # Get workflow based on document type
        workflow = self._get_workflow_based_on_document_type(document_type)

        # RL Environment setup
        env = WorkflowEnvironment()
        current_state = env.reset()
        action, _ = model.predict(current_state, deterministic=True)

        # Clip action to valid range
        num_managers = len(env.managers)
        action = min(action, num_managers - 1)
        try:
            selected_manager = env.managers[action-1]
        except IndexError:
            raise ValidationError(f"Invalid action: {action}. Check RL environment setup.")

        # Create workflow instance
        workflow_instance = WorkflowInstance.objects.create(
            workflow=workflow,
            document=document,
            performed_by=selected_manager,
            current_stage="Review Document",
            status="In Progress"
        )

        # Link workflow instance to document
        document.workflow_instance = workflow_instance
        document.save()

    def _get_workflow_based_on_document_type(self, document_type):
        """Return workflow object based on document type."""
        workflows = {
            "Report": "Report",
            "Invoice": "invoice",
            "Contract": "Contract"
        }
        try:
            return Workflow.objects.get(name=workflows[document_type])
        except Workflow.DoesNotExist:
            raise ValidationError(f"Workflow for '{document_type}' not found.")