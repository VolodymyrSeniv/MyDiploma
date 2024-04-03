from django.db import models
from django.contrib.auth.models import AbstractUser
from gitlab_service import settings
from django.urls import reverse


# Create your models here.
class Teacher(AbstractUser): #teacher database model
    gitlab_id = models.CharField(max_length=255, unique=True)
    access_token = models.CharField(max_length=255, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} - {self.gitlab_id}"


class Student(models.Model): #student database model
    gitlab_id = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=100)
    second_name = models.CharField(max_length = 100)
    email = models.EmailField()

    class Meta:
        ordering = ["-first_name"]

    def __str__(self):
        return f"{self.first_name} - {self.second_name}"


class Classroom(models.Model): #classroom database model
    title = models.CharField(max_length=255, unique=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    organization = models.CharField(max_length=255, blank=False)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, 
        related_name="classroom"
        )
    students = models.ManyToManyField(Student, related_name="classroom")

    class Meta:#ordering
        ordering = ["-creation_date"]

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):#getting the url
        return reverse("gitlab:classroom-detail", args=[str(self.id)])


class Assignment(models.Model): #assigment database model
    title = models.CharField(max_length=255, unique=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    deadline = models.DateTimeField(help_text="The deadline for submitting this assignment.")
    repo_url = models.URLField()
    students = models.ManyToManyField(Student, related_name="assignment")
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assignment"
        )
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name="assignment"
        )

    class Meta:
        ordering = ['-creation_date']

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):#getting the url
        return reverse("gitlab:assignment-detail", args=[str(self.id)])


class Submission(models.Model): #model for assigment submission
    submission_date = models.DateField()
    grade = models.CharField(max_length=2)
    submission_link = models.URLField()
    feedback = models.TextField(
        blank=True,
        help_text="Feedback provided for the submission."
        )
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submission"
        )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="submission"
        )

    class Meta:
        unique_together = ('assignment', 'student')
        ordering = ['-submission_date']

    def __str__(self):
        return f"{self.student.name} - {self.assignment.title} - {self.grade}"