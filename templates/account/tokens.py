from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, new_user, timestamp):
        return (
            six.text_type(new_user.pk) + six.text_type(timestamp) +
            six.text_type(new_user.is_active)
        )

account_activation_token = TokenGenerator()