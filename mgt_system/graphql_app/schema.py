import graphene
from graphene_django.types import DjangoObjectType
from documents.models import Document, Workflow, WorkflowStage, WorkflowInstance, StageTransition
from django.contrib.auth.models import User

import logging
logging.basicConfig(level=logging.DEBUG)
import torch



#shema
# Define User Type
class UserType(DjangoObjectType):
    class Meta:
        model = User

# Define WorkflowInstance Type
class WorkflowInstanceType(DjangoObjectType):
    class Meta:
        model = WorkflowInstance

# Define Document Type
class DocumentType(DjangoObjectType):
    class Meta:
        model = Document

    workflow_instance = graphene.Field(WorkflowInstanceType)  # Match snake_case field name

    def resolve_workflow_instance(self, info):
        # Debugging
        print(f"Resolving workflow_instance for document ID: {self.id}")
        return self.workflow_instance  # ORM uses snake_case

# Define Workflow Type
# Define Workflow Type
class WorkflowType(DjangoObjectType):
    class Meta:
        model = Workflow

    createdBy = graphene.Field(UserType)  # Use camelCase for created_by
    documents = graphene.List(DocumentType)
    instances = graphene.List(WorkflowInstanceType)  # Add instances explicitly

    def resolve_createdBy(self, info):
        return self.created_by

    def resolve_documents(self, info):
        # Fetch documents linked to this workflow via workflow instances
        workflow_instances = self.instances.all()
        return Document.objects.filter(workflow_instance__in=workflow_instances)

    def resolve_instances(self, info):
        # Fetch all workflow instances related to this workflow
        return self.instances.all()


# Define WorkflowStage Type
class WorkflowStageType(DjangoObjectType):
    class Meta:
        model = WorkflowStage

# Define StageTransition Type
class StageTransitionType(DjangoObjectType):
    class Meta:
        model = StageTransition
##########################################################################################################################

# Queries
class Query(graphene.ObjectType):
    workflows = graphene.List(WorkflowType)
    documents = graphene.List(DocumentType)
    workflow_instances = graphene.List(WorkflowInstanceType)
    users = graphene.List(UserType)

    documents_by_status = graphene.List(DocumentType, status=graphene.String())
    workflow_with_users = graphene.Field(WorkflowType, id=graphene.Int())
###########################################################################


##############################################################################################""


    def resolve_workflows(self, info):
        print("Resolving workflows")
        try:
            return Workflow.objects.prefetch_related('created_by', 'instances').all()
        except Exception as e:
            print(f"Error: {e}")
            return []



    def resolve_documents(self, info):
        doc = Document.objects.get(id=5)
        print(doc.workflow_instance)
        return Document.objects.all()

    def resolve_workflow_instances(self, info):
        """
        Fetch all workflow instances. Ensure proper filtering and prefetching.
        """
        try:
            # Fetch all workflow instances with related data
            return WorkflowInstance.objects.select_related('performed_by', 'document', 'workflow').all()
        except Exception as e:
            logging.error(f"Error fetching workflow instances: {e}")
            return None

    def resolve_users(self, info):
        return User.objects.all()

    def resolve_documents_by_status(self, info, status):
        return Document.objects.filter(status=status)

    def resolve_workflow_with_users(self, info, id):
        return Workflow.objects.prefetch_related('created_by').get(id=id)

# Mutations
class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserType)

    def mutate(self, info, username, email, password):
        user = User(username=username, email=email)
        user.set_password(password)  # Hash the password
        user.save()
        return CreateUser(user=user)


class UpdateUser(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        username = graphene.String()
        email = graphene.String()
        password = graphene.String()

    user = graphene.Field(UserType)

    def mutate(self, info, id, username=None, email=None, password=None):
        user = User.objects.get(pk=id)
        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.set_password(password)  # Update hashed password
        user.save()
        return UpdateUser(user=user)


class DeleteUser(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        user = User.objects.get(pk=id)
        user.delete()
        return DeleteUser(success=True)
    

class CreateWorkflow(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String()

    workflow = graphene.Field(WorkflowType)

    def mutate(self, info, name, description="Default description"):
        workflow = Workflow(name=name, description=description)
        workflow.save()
        return CreateWorkflow(workflow=workflow)


class UpdateWorkflow(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        description = graphene.String()

    workflow = graphene.Field(WorkflowType)

    def mutate(self, info, id, name=None, description=None):
        workflow = Workflow.objects.get(pk=id)
        if name:
            workflow.name = name
        if description:
            workflow.description = description
        workflow.save()
        return UpdateWorkflow(workflow=workflow)


class DeleteWorkflow(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        workflow = Workflow.objects.get(pk=id)
        workflow.delete()
        return DeleteWorkflow(success=True)
class CreateDocument(graphene.Mutation):
    class Arguments:
        title = graphene.String()
        content = graphene.String()
        type = graphene.String()

    document = graphene.Field(lambda: DocumentType)

    def mutate(self, info, title, content, type):
        document = Document.objects.create(title=title, content=content, type=type)
        return CreateDocument(document=document)

class UpdateDocument(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        title = graphene.String()
        content = graphene.String()

    document = graphene.Field(lambda: DocumentType)

    def mutate(self, info, id, title=None, content=None):
        document = Document.objects.get(pk=id)
        if title:
            document.title = title
        if content:
            document.content = content
        document.save()
        return UpdateDocument(document=document)

class DeleteDocument(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            document = Document.objects.get(pk=id)
            document.delete()
            return DeleteDocument(success=True)
        except Document.DoesNotExist:
            return DeleteDocument(success=False)

class Mutation(graphene.ObjectType):
# workflow mutations

    create_workflow = CreateWorkflow.Field()
    update_workflow = UpdateWorkflow.Field()
    delete_workflow = DeleteWorkflow.Field()
# User mutations
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()
# doc mutations

    create_document = CreateDocument.Field()
    update_document = UpdateDocument.Field()
    delete_document = DeleteDocument.Field()

# Schema
schema = graphene.Schema(query=Query, mutation=Mutation)



"""
query GetDocumentsByStatus($status: String!) {
  documentsByStatus(status: $status) {
    id
    title
    status
    type
    createdAt
    uploadedBy {  # Fetch the uploader of the document
      id
      username
      email
    }
    workflowInstance {  # Fetch associated workflow instance
      id
      status
      currentStage
      workflow {  # Fetch the workflow for the instance
        id
        name
        description
      }
    }
  }
}


{
  "status": "Submitted"
}


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
query GetWorkflowWithInstances($id: Int!) {
  workflowWithUsers(id: $id) {
    id
    name
    description
    createdBy {  
      id
      username
      email
    }
    instances {  
      id
      status
      currentStage
      createdAt
      performedBy {
        id
        username
      }
      document {  
        id
        title
        status
      }
    }
  }
}

{
  "id": 4
}

""""""""""""""""""""""""""""""""""""""After adding the resolver, the following query will fetch all WorkflowInstance entries, including their related manager (performedBy), document, and workflow details.""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

query {
  workflowInstances {
    id
    status
    currentStage
    performedBy {  # Manager assigned to this workflow instance
      id
      username
    }
    document {  # Document associated with this instance
      id
      title
      status
    }
    workflow {  # Workflow associated with this instance
      id
      name
    }
  }
}
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

mutation CreateWorkflow($name: String!, $description: String!) {
  createWorkflow(name: $name, description: $description) {
    workflow {
      id
      name
      description
    }
  }
}

{
  "name": "Invoice Approval",
  "description": "Workflow for approving invoices"
}


"""


##################################################################################################################


"""import graphene
from graphene_django.types import DjangoObjectType
from documents.models import Document, Workflow
from django.contrib.auth.models import User  # Use built-in User model

class DocumentType(DjangoObjectType):
    class Meta:
        model = Document

class WorkflowType(DjangoObjectType):
    class Meta:
        model = Workflow

class UserType(DjangoObjectType):
    class Meta:
        model = User  # Use built-in User model

class Query(graphene.ObjectType):
    all_documents = graphene.List(DocumentType)
    all_workflows = graphene.List(WorkflowType)
    all_users = graphene.List(UserType)

    def resolve_all_documents(self, info, **kwargs):
        return Document.objects.all()

    def resolve_all_workflows(self, info, **kwargs):
        return Workflow.objects.all()

    def resolve_all_users(self, info, **kwargs):
        return User.objects.all()  # Built-in User model query

class CreateDocument(graphene.Mutation):
    class Arguments:
        title = graphene.String()
        content = graphene.String()
        type = graphene.String()

    document = graphene.Field(lambda: DocumentType)

    def mutate(self, info, title, content, type):
        document = Document.objects.create(title=title, content=content, type=type)
        return CreateDocument(document=document)

class UpdateDocument(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        title = graphene.String()
        content = graphene.String()

    document = graphene.Field(lambda: DocumentType)

    def mutate(self, info, id, title=None, content=None):
        document = Document.objects.get(pk=id)
        if title:
            document.title = title
        if content:
            document.content = content
        document.save()
        return UpdateDocument(document=document)

class DeleteDocument(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            document = Document.objects.get(pk=id)
            document.delete()
            return DeleteDocument(success=True)
        except Document.DoesNotExist:
            return DeleteDocument(success=False)

class Mutation(graphene.ObjectType):
    create_document = CreateDocument.Field()
    update_document = UpdateDocument.Field()
    delete_document = DeleteDocument.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
"""