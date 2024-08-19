from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
import gitlab

class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('accounts:login')
        self.user_model = get_user_model()
        self.access_token = 'test_access_token'
        self.gitlab_id = '12345'
        self.username = 'testuser'
        
        # Create a mock user in the database
        self.user = self.user_model.objects.create(
            gitlab_id=self.gitlab_id,
            username=self.username
        )

    @patch('gitlab.Gitlab')
    def test_login_view_post_success(self, MockGitlab):
        # Mock GitLab user
        mock_gitlab_instance = MockGitlab.return_value
        mock_gitlab_instance.user.id = self.gitlab_id
        mock_gitlab_instance.user.username = self.username
        mock_gitlab_instance.user.avatar_url = 'http://example.com/avatar.png'
        mock_gitlab_instance.user.email = 'testuser@example.com'
        mock_gitlab_instance.auth.return_value = None  # Mock the auth method to do nothing

        response = self.client.post(self.login_url, {'access_token': self.access_token})

        # Check if the response is a redirect to the index page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gitlab_classroom:index'))
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_login_view_get(self):
        # Test GET request to login view
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_login_view_post_invalid_token(self):
        # Test POST request with invalid token
        response = self.client.post(self.login_url, {'access_token': 'invalid_token'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertContains(response, 'Invalid access token')

    def test_login_view_post_no_token(self):
        # Test POST request without token
        response = self.client.post(self.login_url, {'access_token': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertContains(response, 'Access token is required')
