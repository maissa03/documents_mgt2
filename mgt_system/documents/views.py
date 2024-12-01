from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Document, Workflow
from .serializers import DocumentSerializer, WorkflowSerializer



class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

class WorkflowViewSet(viewsets.ModelViewSet):
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer


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
