
from rest_framework import serializers
from .models import Workflow, Document, WorkflowStage, WorkflowInstance, StageTransition

"""

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'title', 'content', 'type', 'status', 'uploaded_by', 'workflow_instance','file_path','created_at']
        read_only_fields = ['uploaded_by','type', 'content','workflow_instance']
"""

class WorkflowInstanceSerializer(serializers.ModelSerializer):
    document_title = serializers.CharField(source='document.title', read_only=True)
    document_content = serializers.CharField(source='document.content', read_only=True)  # Add content
    document_type = serializers.CharField(source='document.type', read_only=True)       # Add type
    document_status = serializers.CharField(source='document.status', read_only=True)   # Add status

    class Meta:
        model = WorkflowInstance
        fields = [
            'id', 'document', 'document_title', 'document_content', 
            'document_type', 'document_status', 'current_stage', 
            'status', 'created_at', 'performed_by'
        ]



class DocumentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='uploaded_by.username', read_only=True)
    workflow_status = serializers.CharField(source='workflow_instance.status', read_only=True)  # Directly access status
    workflow_instance_details = WorkflowInstanceSerializer(source='workflow_instance', read_only=True)  # Include full instance details if needed
    workflow_instance_status = serializers.CharField(source='workflow_instance.status', read_only=True)  
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'content', 'type', 'status', 'uploaded_by',
            'file_path', 'created_at', 'workflow_status', 'workflow_instance_details','workflow_instance_status','user_name',
        ]
        read_only_fields = ['uploaded_by', 'type', 'content', 'workflow_instance','user_name']

class WorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = '__all__'


class WorkflowStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowStage
        fields = '__all__'




class StageTransitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StageTransition
        fields = '__all__'

