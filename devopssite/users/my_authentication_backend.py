from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model


class EmailBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        Model = get_user_model()

        try:
            user = Model.objects.get(email=email)
        except Model.DoesNotExist:
            return None

        if user.check_password(password):
            return user

        return None

    def get_user(self, user_id):
        Model = get_user_model()

        try:
            return Model.objects.get(pk=user_id)
        except Model.DoesNotExist:
            return None
