from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from gitlab_classroom.forms import ForkProjectsForm
from .models import Teacher, Student, Classroom, Assignment
from datetime import datetime
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
import gitlab
import re



# testing models /////////////////////////////////////////////////////
class TeacherModelTest(TestCase):
    def test_string_representation(self):
        teacher = Teacher(first_name="John", gitlab_id="12345")
        self.assertEqual(str(teacher), f"{teacher.first_name} - {teacher.gitlab_id}")

    def test_unique_gitlab_id(self):
        teacher1 = Teacher.objects.create(username="john", gitlab_id="12345")
        with self.assertRaises(Exception):
            teacher2 = Teacher.objects.create(username="jane", gitlab_id="12345")

class StudentModelTest(TestCase):
    def setUp(self):
            self.student = Student.objects.create(
                gitlab_id="12345",
                gitlab_username="john_doe",
                first_name="John",
                second_name="Doe",
                email="john_doe@example.com"
            )

    def test_string_representation(self):
        self.assertEqual(str(self.student), f"{self.student.gitlab_username} - {self.student.gitlab_id}")

    def test_ordering(self):
        student2 = Student.objects.create(
            gitlab_id="67890",
            gitlab_username="jane_doe",
            first_name="Jane",
            second_name="Doe",
            email="jane_doe@example.com"
        )
        students = Student.objects.all().order_by('-first_name')
        self.assertEqual(students[0], self.student)
        self.assertEqual(students[1], student2)


    def test_get_absolute_url(self):
        self.assertEqual(self.student.get_absolute_url(), reverse('gitlab_classroom:student-detail', args=[str(self.student.id)]))

class ClassroomModelTest(TestCase):
    def setUp(self):
        self.teacher = get_user_model().objects.create_user(username="teacher", gitlab_id="12345")
        self.classroom = Classroom.objects.create(
            title="Test Classroom",
            description="A classroom for testing.",
            organization="Test Organization",
            teacher=self.teacher
        )

    def test_string_representation(self):
        self.assertEqual(str(self.classroom), self.classroom.title)

    def test_ordering(self):
        classroom2 = Classroom.objects.create(
            title="Another Classroom",
            description="Another classroom for testing.",
            organization="Test Organization",
            teacher=self.teacher
        )
        classrooms = Classroom.objects.all().order_by('-creation_date')
        self.assertEqual(classrooms[0], self.classroom)
        self.assertEqual(classrooms[1], classroom2)


    def test_get_absolute_url(self):
        self.assertEqual(self.classroom.get_absolute_url(), reverse('gitlab_classroom:classroom-detail', args=[str(self.classroom.id)]))

class AssignmentModelTest(TestCase):
    def setUp(self):
        self.teacher = Teacher.objects.create_user(username='teacher', password='pass')
        self.classroom = Classroom.objects.create(
            title="Test Classroom",
            description="A classroom for testing.",
            organization="Test Organization",
            teacher=self.teacher
        )
        self.assignment = Assignment.objects.create(
            title="Test Assignment",
            description="An assignment for testing.",
            deadline=timezone.now(),
            repo_url="http://example.com/repo",
            teacher=self.teacher,
            classroom=self.classroom,
            creation_date=timezone.now() - timezone.timedelta(days=1)  # Set creation_date explicitly
        )

    def test_string_representation(self):
        self.assertEqual(str(self.assignment), self.assignment.title)

    def test_ordering(self):
        assignment2 = Assignment.objects.create(
            title="Another Assignment",
            description="Another assignment for testing.",
            deadline=timezone.now(),
            repo_url="http://example.com/repo2",
            teacher=self.teacher,
            classroom=self.classroom,
            creation_date=timezone.now()  # Set creation_date explicitly
        )
        assignments = list(Assignment.objects.all())
        self.assertEqual(assignments[0], self.assignment)
        self.assertEqual(assignments[1], assignment2)

    def test_get_absolute_url(self):
        self.assertEqual(self.assignment.get_absolute_url(), reverse('gitlab_classroom:assignment-detail', args=[str(self.assignment.id)]))
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# testing views /////////////////////////////////////////////////////////////////////////////
User = get_user_model()

class ClassroomCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.url = reverse('gitlab_classroom:classroom-create')
        self.data = {
            'title': 'Test Classroom',
            'description': 'A classroom for testing.',
            'organization': 'Test Organization'
        }
        self.access_token = 'testtoken'

    @patch('gitlab.Gitlab.http_post')
    def test_create_classroom(self, mock_http_post):
        # Add access_token to session
        session = self.client.session
        session['access_token'] = self.access_token
        session.save()

        # Mock GitLab group creation responses
        mock_http_post.side_effect = [
            {'id': 1, 'name': self.data['title'], 'path': re.sub(r'[^a-zA-Z0-9_\-.]', '_', self.data['title'].lower()).strip('-.'), 'description': self.data['description']},
            {'id': 2, 'name': 'MEMBERS', 'path': f"{re.sub(r'[^a-zA-Z0-9_\-.]', '_', self.data['title'].lower()).strip('-.')}_MEMBERS", 'description': 'Classroom Members', 'parent_id': 1},
            {'id': 3, 'name': 'ASSIGNMENTS', 'path': f"{re.sub(r'[^a-zA-Z0-9_\-.]', '_', self.data['title'].lower()).strip('-.')}_ASSIGNMENTS", 'description': 'Assignments folder', 'parent_id': 1}
        ]

        # Test the POST request
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 302)  # Should redirect after success

        # Check if the classroom object was created in the database
        classroom = Classroom.objects.get(title='Test Classroom')
        self.assertIsNotNone(classroom)
        self.assertEqual(classroom.description, 'A classroom for testing.')
        self.assertEqual(classroom.organization, 'Test Organization')
        self.assertEqual(classroom.teacher, self.user)

        # Check if the GitLab group was created with sanitized path
        sanitized_title = re.sub(r'[^a-zA-Z0-9_\-.]', '_', self.data['title'].lower()).strip('-.')
        
        # Verify the actual calls made to http_post
        mock_http_post.assert_any_call(
            '/groups',
            post_data={
                'name': self.data['title'],
                'path': sanitized_title,
                'description': self.data['description']
            },
            files={}
        )
        
        # Check if the GitLab subgroups were created
        members_path = f"{sanitized_title}_MEMBERS".strip('-.')
        assignments_path = f"{sanitized_title}_ASSIGNMENTS".strip('-.')
        mock_http_post.assert_any_call(
            '/groups',
            post_data={
                'name': 'MEMBERS',
                'path': members_path,
                'description': 'Classroom Members',
                'parent_id': 1
            },
            files={}
        )
        mock_http_post.assert_any_call(
            '/groups',
            post_data={
                'name': 'ASSIGNMENTS',
                'path': assignments_path,
                'description': 'Assignments folder',
                'parent_id': 1
            },
            files={}
        )

        # Ensure the classroom object was updated with the GitLab group ID
        classroom.refresh_from_db()
        self.assertEqual(classroom.gitlab_id, 1)
    

User = get_user_model()

class AssignmentsDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.classroom = Classroom.objects.create(
            title='Test Classroom',
            description='A classroom for testing.',
            organization='Test Organization',
            teacher=self.user,
            gitlab_id=123
        )
        self.assignment = Assignment.objects.create(
            title='Test Assignment',
            description='An assignment for testing.',
            deadline='2024-12-31 23:59:59',
            repo_url='https://gitlab.com/test/repo',
            teacher=self.user,
            classroom=self.classroom,
            gitlab_id=456
        )
        self.url = reverse('gitlab_classroom:assignment-detail', kwargs={'pk': self.assignment.pk})
        self.access_token = 'testtoken'

    @patch('gitlab.Gitlab')
    def test_get_context_data(self, mock_gitlab):
        session = self.client.session
        session['access_token'] = self.access_token
        session.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('fork_projects_form', response.context)
        self.assertIsInstance(response.context['fork_projects_form'], ForkProjectsForm)

    @patch('gitlab.Gitlab')
    def test_post_valid_form(self, mock_gitlab):
        session = self.client.session
        session['access_token'] = self.access_token
        session.save()

        mock_gl_instance = mock_gitlab.return_value
        mock_group = MagicMock()
        mock_gl_instance.groups.get.return_value = mock_group
        mock_group.subgroups.list.return_value = []
        mock_group.id = 789
        mock_gl_instance.projects.get.return_value.forks.create.return_value.id = 101112

        data = {
            'gitlab_template_id': '789'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.assignment.get_absolute_url())

    @patch('gitlab.Gitlab')
    def test_post_invalid_form(self, mock_gitlab):
        session = self.client.session
        session['access_token'] = self.access_token
        session.save()

        data = {
            'gitlab_template_id': ''  # Invalid form data
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)  # Assuming it redirects even on invalid form
        self.assertRedirects(response, self.assignment.get_absolute_url())


User = get_user_model()


class ClassroomCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.url = reverse('gitlab_classroom:classroom-create')
        self.data = {
            'title': 'Test Classroom',
            'description': 'A classroom for testing.',
            'organization': 'Test Org'
        }
        session = self.client.session
        session['access_token'] = 'fake-token'
        session.save()

    @patch('gitlab.Gitlab')
    def test_create_classroom(self, MockGitlab):
        mock_gl_instance = MockGitlab.return_value
        mock_group = MagicMock()
        mock_group.id = 1
        mock_gl_instance.groups.create.return_value = mock_group

        response = self.client.post(self.url, self.data)
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Classroom.objects.filter(title='Test Classroom').exists())
        mock_gl_instance.groups.create.assert_any_call({
            'name': 'Test Classroom',
            'path': 'test_classroom',
            'description': 'A classroom for testing.'
        })
        mock_gl_instance.groups.create.assert_any_call({
            'name': 'MEMBERS',
            'path': 'test_classroom_MEMBERS',
            'description': 'Classroom Members',
            'parent_id': 1
        })
        mock_gl_instance.groups.create.assert_any_call({
            'name': 'ASSIGNMENTS',
            'path': 'test_classroom_ASSIGNMENTS',
            'description': 'Assignments folder',
            'parent_id': 1
        })


    @patch('gitlab.Gitlab')
    def test_create_classroom_gitlab_error(self, MockGitlab):
        mock_gl_instance = MockGitlab.return_value
        mock_gl_instance.groups.create.side_effect = gitlab.exceptions.GitlabCreateError

        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 500)
        self.assertFalse(Classroom.objects.filter(title='Test Classroom').exists())