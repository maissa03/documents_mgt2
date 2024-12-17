'''from spyne import Application, rpc, ServiceBase, String, Iterable, ByteArray
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoApplication
import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import xml.etree.ElementTree as ET

import base64
import requests

REST_API_URL = "http://127.0.0.1:8000/documents/"
REST_API_USERNAME = "missou"
REST_API_PASSWORD = "admin"



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
            data = {'uploaded_by': 1}  # Assuming 1 is the ID of the admin user
            
            # Encode credentials
            credentials = f"{REST_API_USERNAME}:{REST_API_PASSWORD}"
            base64_credentials = base64.b64encode(credentials.encode()).decode()
            headers = {'Authorization': f'Basic {base64_credentials}'}
            
            # Send the file to the REST API
            rest_response = requests.post(REST_API_URL, files=files, data=data, headers=headers)
            if rest_response.status_code == 201:  # Created
                return f"Document '{document_name}' successfully sent to REST API."
            else:
                return f"Failed to send document to REST API: {rest_response.status_code}, {rest_response.text}"
        else:
            return f"Failed to fetch document from Nextcloud: {response.status_code}, {response.text}"


# SOAP Application Setup
application = Application(
    [LegacyDocumentService],
    tns='legacy_integration.soap',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

soap_app = DjangoApplication(application)
access_soap_app = csrf_exempt(soap_app)
'''

# SOAP Service to manage legacy documents via Nextcloud and REST
import base64
from spyne import Application, rpc, ServiceBase, String, Iterable, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoApplication
import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import xml.etree.ElementTree as ET

REST_API_URL = "http://127.0.0.1:8000/handle_soap_document/"
REST_API_USERNAME = "missou"
REST_API_PASSWORD = "admin"

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
            for href in root.findall('.//{DAV:}href'):
                document_path = href.text
                if document_path.endswith("/"):  # Skip directories
                    continue
                document_name = document_path.split("/")[-1]
                documents.append(document_name)
            return documents
        else:
            raise Exception(f"Failed to fetch document list: {response.status_code}, {response.text}")

     # 2. **Fetch PDF Content**
    @rpc(String, _returns=Unicode)
    def get_pdf_content(ctx, document_name):
        """Fetch the content of a PDF document."""
        file_url = f"{NEXTCLOUD_URL}/{NEXTCLOUD_USERNAME}/legacy_documents/{document_name}"
        response = requests.get(file_url, auth=HTTPBasicAuth(NEXTCLOUD_USERNAME, NEXTCLOUD_PASSWORD))
        if response.status_code == 200:
            return base64.b64encode(response.content).decode('utf-8')  # Return PDF content as Base64
        else:
            raise Exception(f"Failed to fetch document: {response.status_code}, {response.text}")

    # 3. **Upload PDF Document**
    @rpc(String, Unicode, _returns=String)
    def create_pdf_document(ctx, document_name, content):
        """Upload a new PDF document to Nextcloud."""
        if not document_name.endswith(".pdf"):
            raise Exception("Document must have a '.pdf' extension.")

        file_url = f"{NEXTCLOUD_URL}/{NEXTCLOUD_USERNAME}/legacy_documents/{document_name}"

        try:
            # Decode the Base64 content
            file_content = base64.b64decode(content)
            print(f"Decoded file content length: {len(file_content)} bytes")  # Debugging
        except Exception as e:
            raise Exception(f"Failed to decode content: {str(e)}")

        # Upload the decoded content to Nextcloud
        headers = {"Content-Type": "application/octet-stream"}  # Ensure binary upload
        response = requests.put(
            file_url,
            data=file_content,
            auth=HTTPBasicAuth(NEXTCLOUD_USERNAME, NEXTCLOUD_PASSWORD),
            headers=headers
        )

        if response.status_code in [201, 204]:
            return f"PDF document '{document_name}' successfully uploaded."
        else:
            print("Nextcloud Response:", response.status_code, response.text)  # Debugging
            raise Exception(f"Failed to upload document: {response.status_code}, {response.text}")

    # 4. **Update PDF Document**
    @rpc(String, Unicode, _returns=String)
    def update_pdf_document(ctx, document_name, content):
        """Update the content of an existing PDF document."""
        return LegacyDocumentService.create_pdf_document(ctx, document_name, content)

    # 5. **Delete PDF Document**
    @rpc(String, _returns=String)
    def delete_pdf_document(ctx, document_name):
        """Delete a PDF document from Nextcloud."""
        file_url = f"{NEXTCLOUD_URL}/{NEXTCLOUD_USERNAME}/legacy_documents/{document_name}"
        response = requests.delete(file_url, auth=HTTPBasicAuth(NEXTCLOUD_USERNAME, NEXTCLOUD_PASSWORD))
        if response.status_code == 204:  # No Content = Successfully Deleted
            return f"PDF document '{document_name}' successfully deleted."
        else:
            raise Exception(f"Failed to delete document: {response.status_code}, {response.text}")



    #SEND TO REST 
    @rpc(String, _returns=String)
    def send_document_to_rest(ctx, document_name):
        """Send document to REST API."""
        file_url = f"{NEXTCLOUD_URL}/{NEXTCLOUD_USERNAME}/legacy_documents/{document_name}"
        
        # Fetch the file content from Nextcloud
        response = requests.get(file_url, auth=HTTPBasicAuth(NEXTCLOUD_USERNAME, NEXTCLOUD_PASSWORD))
        if response.status_code == 200:
            file_content = base64.b64encode(response.content).decode('utf-8')  # Encode content as Base64

            # Prepare REST API request payload
            data = {
                "document_name": document_name,
                "content": file_content,  # Base64-encoded content
            }
            headers = {
                "Authorization": f"Basic {base64.b64encode(f'{REST_API_USERNAME}:{REST_API_PASSWORD}'.encode()).decode()}",
                "Content-Type": "application/json"
            }

            # Send the file content to the REST API
            rest_response = requests.post(REST_API_URL, json=data, headers=headers)
            if rest_response.status_code == 201:
                return f"Document '{document_name}' successfully sent to REST API."
            else:
                return f"Failed to send document to REST API: {rest_response.status_code}, {rest_response.text}"
        else:
            return f"Failed to fetch document from Nextcloud: {response.status_code}, {response.text}"


# Create the SOAP application
application = Application(
    [LegacyDocumentService],
    'spyne.examples.legacy_document',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

# Create the Django application
legacy_document_service_app = csrf_exempt(DjangoApplication(application))
