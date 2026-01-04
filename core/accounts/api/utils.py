from rest_framework_simplejwt.tokens import RefreshToken
import threading

# Background thread for sending email without blocking the request.
class EmailThread(threading.Thread):
    def __init__(self,email_obj):
        # Store the email object for async sending.
        threading.Thread.__init__(self)
        self.email_obj = email_obj
    def run(self):
        # Send the email when the thread executes.
        self.email_obj.send()

#mixin for getting a token for user!
class TokenForUserMixin:
    def get_tokens_for_user(self, user):
        # Generate a refresh token string for the given user.
        refresh = RefreshToken.for_user(user)
        return str(refresh)
