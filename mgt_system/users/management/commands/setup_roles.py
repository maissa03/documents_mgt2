# users/management/commands/setup_roles.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from users.models import CustomUser  # Replace with the actual path if different

class Command(BaseCommand):
    help = 'Sets up initial roles and permissions'

    def handle(self, *args, **kwargs):
        # Create groups
        admin_group, created = Group.objects.get_or_create(name='Administrator')
        manager_group, created = Group.objects.get_or_create(name='Manager')
        employee_group, created = Group.objects.get_or_create(name='Employee')

        # Create custom permissions (ensure they match your model definition)
        content_type = ContentType.objects.get(app_label='users', model='document')
        permission_add_document, created = Permission.objects.get_or_create(
            codename='custom_add_document',
            name='Can custom add document',
            content_type=content_type
        )
        permission_view_document, created = Permission.objects.get_or_create(
            codename='custom_view_document',
            name='Can custom view document',
            content_type=content_type
        )

        # Assign permissions to the groups
        admin_group.permissions.add(permission_add_document, permission_view_document)
        manager_group.permissions.add(permission_view_document)

        self.stdout.write(self.style.SUCCESS('Roles and permissions have been set up successfully!'))
