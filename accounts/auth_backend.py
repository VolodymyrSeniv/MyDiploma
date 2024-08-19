from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model


class GitLabAuthBackend(BaseBackend):
    def authenticate(self, request, gitlab_id=None, username=None):
        UserModel = get_user_model()
        try:
            # Attempt to get the existing user
            user = UserModel.objects.get(gitlab_id=gitlab_id)
            return user
        except UserModel.DoesNotExist:
            # If the user does not exist, create a new one
            user = UserModel.objects.create(
                gitlab_id=gitlab_id,
                username=username
            )
            return user

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
