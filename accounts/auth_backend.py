from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

#here I rewrite the authentication backends
class GitLabAuthBackend(BaseBackend):
    def authenticate(self, request, gitlab_id=None):
        UserModel = get_user_model()
        user, created = UserModel.objects.get_or_create(
            gitlab_id=gitlab_id,
        )
        return user

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
