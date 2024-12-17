from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .soap_services import LegacyDocumentService
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoApplication
import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from zeep import Client, Fault

class LegacyDocumentView(APIView):
    
    def post(self, request):
        """Send a document to the REST API via the SOAP service."""
        document_name = request.data.get("document_name")
        if not document_name:
            return Response({"error": "Document name is required."}, status=400)

        try:
            # Set up the SOAP client
            client = Client("http://127.0.0.1:8000/soap/?wsdl")

            # Call the send_document_to_rest method
            result = client.service.send_document_to_rest(document_name)

            return Response({"message": result}, status=200)

        except Fault as e:
            return Response({"error": f"SOAP Fault: {e}"}, status=500)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
    
    def get(self, request):
        """Fetch and integrate legacy documents."""
        service = LegacyDocumentService()

        try:
            # Step 1: Fetch legacy documents via SOAP service
            legacy_documents = service.get_document_list()
            integrated_documents = []

            # Step 2: Process and integrate each document (simulating integration)
            for doc in legacy_documents:
                # Here we assume 'integrate_legacy_document' is a method you want to implement
                # You can adjust this as per the exact functionality you need.
                integrated_document = doc  # Just use doc for now
                integrated_documents.append(integrated_document)

            return Response({
                "message": "Legacy documents integrated successfully.",
                "documents": integrated_documents
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)
  
    def delete(self, request, document_id):
        """Delete a legacy document via SOAP."""
        service = LegacyDocumentService()

        try:
            # Step 1: Call SOAP service to delete the document
            result = service.delete_document(document_id)

            # Return appropriate response
            return Response({
                "message": f"Legacy document {document_id} deleted successfully.",
                "result": result
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)
