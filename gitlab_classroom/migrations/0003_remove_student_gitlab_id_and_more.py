# Generated by Django 4.2.7 on 2024-04-19 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gitlab_classroom', '0002_student_gitlab_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='gitlab_id',
        ),
        migrations.AlterField(
            model_name='student',
            name='gitlab_username',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
