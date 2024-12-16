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
from users.views import UserViewSet
from documents.views import DocumentViewSet, WorkflowViewSet
from rest_framework.routers import DefaultRouter
from legacy_soap.soap_services import access_soap_app
router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('users/', include('users.urls')),
    path('api/', include(router.urls)), 
    path('documents/', include('documents.urls')),
    path('graphql/', GraphQLView.as_view(graphiql=True, schema=schema)), 
    path('soap/', access_soap_app),
]

