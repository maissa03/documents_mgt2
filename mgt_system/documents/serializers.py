from rest_framework import serializers
from .models import Document, Workflow


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'


class WorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = '__all__'
