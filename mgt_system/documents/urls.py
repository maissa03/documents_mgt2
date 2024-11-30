from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, WorkflowViewSet

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'workflows', WorkflowViewSet, basename='workflow')

urlpatterns = [
    path('', include(router.urls)),
]
