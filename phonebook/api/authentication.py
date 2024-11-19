from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

class PhoneNumberBackend(BaseBackend):
    def authenticate(self, request, phone_number=None, password=None, **kwargs):
        try:
            user = get_user_model().objects.get(phone_number=phone_number)
            if user.check_password(password):
                return user
        except get_user_model().DoesNotExist:
            return None
        return None
