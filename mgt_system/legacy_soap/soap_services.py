from spyne import Application, rpc, ServiceBase, String, Iterable, ByteArray
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoApplication
import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import xml.etree.ElementTree as ET
import base64

NEXTCLOUD_URL = "https://use08.thegood.cloud/remote.php/dav/files"
NEXTCLOUD_USERNAME = "maalejmaissa7@gmail.com"
NEXTCLOUD_PASSWORD = "Qb#M5!Xz@A@kX.f"

class LegacyDocumentService(ServiceBase):
    """SOAP Service to manage legacy documents via Nextcloud and REST."""

    # 1. **Fetch Document List**
    @rpc(_returns=Iterable(String))
    def get_document_list(ctx):
        """Fetch the list of documents from Nextcloud."""
        response = requests.request(
            "PROPFIND",
            f"{NEXTCLOUD_URL}/{NEXTCLOUD_USERNAME}/legacy_documents/",
            auth=HTTPBasicAuth(NEXTCLOUD_USERNAME, NEXTCLOUD_PASSWORD)
        )
        if response.status_code == 207:  # Multi-status success
            documents = []
            # Parse the XML response to handle namespaces
            root = ET.fromstring(response.text)
            
            # Iterate over all href elements with namespace handling
            for href in root.findall('.//{DAV:}href'):  # Adjust namespace URI accordingly
                name = href.text.split('/')[-1]  # Extract document name
                documents.append(name)

            return documents
        else:
            return ["Failed to retrieve documents"]

    # 2. **Retrieve Document Content**
    @rpc(String, _returns=ByteArray)
    def get_document_content(ctx, document_name):
        """Fetch the content of a specific document from Nextcloud."""
        
        file_url = f"{NEXTCLOUD_URL}/{NEXTCLOUD_USERNAME}/legacy_documents/{document_name}"
        response = requests.get(file_url, auth=HTTPBasicAuth(NEXTCLOUD_USERNAME, NEXTCLOUD_PASSWORD))
        if response.status_code == 200:
            return response.content
        return b""
        

    # 3. **Create (Upload) Document**
    @rpc(String, ByteArray, _returns=String)
    def create_document(ctx, document_name, content):
        """Upload a new document to Nextcloud."""
        file_url = f"{NEXTCLOUD_URL}/{NEXTCLOUD_USERNAME}/legacy_documents/{document_name}"
        response = requests.put(file_url, data=content, auth=HTTPBasicAuth(NEXTCLOUD_USERNAME, NEXTCLOUD_PASSWORD))
        if response.status_code in (200, 201):  # 200 = Updated, 201 = Created
            return f"Document '{document_name}' successfully created."
        return f"Failed to create document: {response.status_code}"

    # 4. **Update Document (Replace Content)**
    @rpc(String, ByteArray, _returns=String)
    def update_document(ctx, document_name, new_content):
        """Replace an existing document's content in Nextcloud."""
        file_url = f"{NEXTCLOUD_URL}/{NEXTCLOUD_USERNAME}/legacy_documents/{document_name}"
        response = requests.put(file_url, data=new_content, auth=HTTPBasicAuth(NEXTCLOUD_USERNAME, NEXTCLOUD_PASSWORD))
        if response.status_code == 200:  # Updated
            return f"Document '{document_name}' successfully updated."
        elif response.status_code == 201:  # Created
            return f"Document '{document_name}' did not exist and has been created."
        return f"Failed to update document: {response.status_code}"

    # 5. **Delete Document**
    @rpc(String, _returns=String)
    def delete_document(ctx, document_name):
        """Delete a document from Nextcloud."""
        file_url = f"{NEXTCLOUD_URL}/{NEXTCLOUD_USERNAME}/legacy_documents/{document_name}"
        response = requests.delete(file_url, auth=HTTPBasicAuth(NEXTCLOUD_USERNAME, NEXTCLOUD_PASSWORD))
        if response.status_code == 204:  # No content means successful deletion
            return f"Document '{document_name}' successfully deleted."
        return f"Failed to delete document: {response.status_code}"

    # 6. **Send Document to REST API (Legacy Integration)**
    @rpc(String, _returns=String)
    def send_document_to_rest(ctx, document_name):
        """Fetch a document from Nextcloud and send it to the REST API."""
        file_url = f"{NEXTCLOUD_URL}/{NEXTCLOUD_USERNAME}/legacy_documents/{document_name}"
        
        # Fetch the file from Nextcloud
        response = requests.get(file_url, auth=HTTPBasicAuth(NEXTCLOUD_USERNAME, NEXTCLOUD_PASSWORD))
        if response.status_code == 200:
            files = {'file_path': (document_name, response.content)}
            rest_url = f"{settings.REST_API_URL}/documents/"
            rest_response = requests.post(rest_url, files=files, headers={"Authorization": f"Bearer {settings.REST_API_TOKEN}"} )
            
            if rest_response.status_code == 201:
                return f"Document '{document_name}' successfully sent to REST API."
            else:
                return f"Failed to send document to REST API. Status: {rest_response.status_code}"
        else:
            return f"Failed to retrieve document from Nextcloud: {response.status_code}"


# SOAP Application Setup
application = Application(
    [LegacyDocumentService],
    tns='legacy_integration.soap',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

soap_app = DjangoApplication(application)
access_soap_app = csrf_exempt(soap_app)
