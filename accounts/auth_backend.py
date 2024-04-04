from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
import gitlab_classroom

#here I rewrite the authentication backends
class GitLabAuthBackend(BaseBackend):
    def authenticate(self, request, gitlab_id=None, access_token=None):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(gitlab_id=gitlab_id, access_token=access_token)
            # Additional verification can be added here
            return user
        except UserModel.DoesNotExist:
            return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
