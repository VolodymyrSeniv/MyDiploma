# Generated by Django 4.2.7 on 2024-05-11 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gitlab_classroom', '0008_remove_student_gitlab'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='gl_flag',
            field=models.BooleanField(default=False),
        ),
    ]
