# Generated by Django 5.1.3 on 2024-12-14 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0009_remove_document_workflow_instance_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stagetransition',
            name='from_stage',
            field=models.CharField(blank=True, choices=[('Approve Document', 'Approve Document'), ('Review Document', 'Review Document'), ('Request Changes', 'Request Changes')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='stagetransition',
            name='to_stage',
            field=models.CharField(blank=True, choices=[('Approve Document', 'Approve Document'), ('Review Document', 'Review Document'), ('Request Changes', 'Request Changes')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='workflowinstance',
            name='current_stage',
            field=models.CharField(blank=True, choices=[('Approve Document', 'Approve Document'), ('Review Document', 'Review Document'), ('Request Changes', 'Request Changes')], max_length=50, null=True),
        ),
    ]
