import graphene
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
