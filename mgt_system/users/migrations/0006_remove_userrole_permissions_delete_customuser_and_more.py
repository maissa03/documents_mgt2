# Generated by Django 5.1.3 on 2024-12-03 21:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_customuser_user_role'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userrole',
            name='permissions',
        ),
        migrations.DeleteModel(
            name='CustomUser',
        ),
        migrations.DeleteModel(
            name='UserRole',
        ),
    ]