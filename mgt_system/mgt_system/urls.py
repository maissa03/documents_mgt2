"""
URL configuration for mgt_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import include, path
from graphene_django.views import GraphQLView
from graphql_app.schema import schema
from users.views import UserViewSet,GroupViewSet
from documents.views import DocumentViewSet, WorkflowViewSet,HandleSOAPDocumentView
from rest_framework.routers import DefaultRouter
from legacy_soap.soap_services import legacy_document_service_app
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from django.conf import settings
from django.conf.urls.static import static
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups',GroupViewSet)
urlpatterns = [
    path('users/', include('users.urls')),
    path('api/', include(router.urls)), 
    path('documents/', include('documents.urls')),
    path('graphql/', GraphQLView.as_view(graphiql=True, schema=schema)), 
    path('soap/', legacy_document_service_app),
    path('handle_soap_document/', HandleSOAPDocumentView.as_view(), name='handle_soap_document'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)