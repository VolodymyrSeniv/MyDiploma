# Generated by Django 4.2.7 on 2024-05-11 17:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gitlab_classroom', '0007_student_gitlab_student_student_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='gitlab',
        ),
    ]