from django.contrib.auth.tokens import PasswordResetTokenGenerator


class ActivationTokenGenerator(PasswordResetTokenGenerator):
    timeout = 60 * 60 * 24

    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{user.password}{user.is_active}{timestamp}"


activation_token_generator = ActivationTokenGenerator()
