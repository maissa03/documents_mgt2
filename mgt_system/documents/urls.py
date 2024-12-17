'''from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, WorkflowViewSet

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'workflows', WorkflowViewSet, basename='workflow')

urlpatterns = [
    path('', include(router.urls)),
]'''
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (WorkflowViewSet, DocumentViewSet, 
                    WorkflowStageViewSet, WorkflowInstanceViewSet, HandleSOAPDocumentView,
                    StageTransitionViewSet)

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
#router.register(r'handle_soap_document', HandleSOAPDocumentView, basename='handle_soap_document')
router.register(r'workflows', WorkflowViewSet, basename='workflow')
router.register(r'workflow-stages', WorkflowStageViewSet, basename='workflowstage')
router.register(r'workflow-instances', WorkflowInstanceViewSet, basename='workflowinstance')
router.register(r'stage-transitions', StageTransitionViewSet, basename='stagetransition')

urlpatterns = [
    path('', include(router.urls)),
    #path('assign-workflow/<int:workflow_id>/', AssignWorkflowView.as_view(), name='assign-workflow'),
    #path('documents/handle_soap_document/', HandleSOAPDocumentView.as_view(), name='handle_soap_document'),

]

