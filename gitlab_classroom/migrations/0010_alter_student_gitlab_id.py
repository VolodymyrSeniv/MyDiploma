# Generated by Django 4.2.7 on 2024-05-11 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gitlab_classroom', '0009_student_gl_flag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='gitlab_id',
            field=models.CharField(max_length=255),
        ),
    ]
