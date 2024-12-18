# Generated by Django 5.1.3 on 2024-12-12 17:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0004_remove_document_uploaded_file_document_file_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='content',
        ),
        migrations.RemoveField(
            model_name='document',
            name='file',
        ),
        migrations.RemoveField(
            model_name='document',
            name='uploaded_by',
        ),
        migrations.RemoveField(
            model_name='document',
            name='workflows',
        ),
        migrations.RemoveField(
            model_name='workflow',
            name='step',
        ),
        migrations.AddField(
            model_name='document',
            name='file_path',
            field=models.FileField(default='default/path/to/file.txt', upload_to='documents/'),
        ),
        migrations.AddField(
            model_name='document',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='workflow',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_workflows', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='document',
            name='status',
            field=models.CharField(choices=[('Draft', 'Draft'), ('Submitted', 'Submitted'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], max_length=10),
        ),
        migrations.AlterField(
            model_name='document',
            name='type',
            field=models.CharField(choices=[('Invoice', 'Invoice'), ('Report', 'Report'), ('Contract', 'Contract')], max_length=10),
        ),
        migrations.AlterField(
            model_name='workflow',
            name='description',
            field=models.TextField(),
        ),
        migrations.CreateModel(
            name='WorkflowInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('In Progress', 'In Progress'), ('Completed', 'Completed')], default='In Progress', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('workflow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='instances', to='documents.workflow')),
            ],
        ),
        migrations.AddField(
            model_name='document',
            name='workflow_instance',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='documents.workflowinstance'),
        ),
        migrations.CreateModel(
            name='WorkflowStage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('stage_order', models.IntegerField()),
                ('action_required', models.CharField(max_length=255)),
                ('workflow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stages', to='documents.workflow')),
            ],
        ),
        migrations.AddField(
            model_name='workflowinstance',
            name='current_stage',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='current_instances', to='documents.workflowstage'),
        ),
        migrations.CreateModel(
            name='StageTransition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=255)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('performed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='performed_transitions', to=settings.AUTH_USER_MODEL)),
                ('workflow_instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transitions', to='documents.workflowinstance')),
                ('from_stage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_transitions', to='documents.workflowstage')),
                ('to_stage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_transitions', to='documents.workflowstage')),
            ],
        ),
    ]
