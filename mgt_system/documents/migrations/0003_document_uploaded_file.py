# Generated by Django 5.1.3 on 2024-11-29 21:10

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0002_workflow_alter_document_options_document_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='uploaded_file',
            field=models.FileField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location='uploads/'), upload_to='documents/'),
        ),
    ]
