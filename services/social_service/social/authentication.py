from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class TokenUser:
    is_anonymous = False

    def __init__(self, payload):
        self.id = payload['user_id']
        self.username = payload.get('username', '')
        self.email = payload.get('email', '')
        self.role = payload.get('role', '')
        self.is_active = payload.get('is_active', True)

    @property
    def is_authenticated(self):
        return self.is_active


class ServiceJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = TokenUser(validated_token)
        if not user.is_active:
            raise InvalidToken("User account is disabled.")
        return user
