from rest_framework_simplejwt.tokens import RefreshToken
import threading

class EmailThread(threading.Thread):
    def __init__(self,email_obj):
        threading.Thread.__init__(self)
        self.email_obj = email_obj
    def run(self):
        self.email_obj.send()

#mixin for getting a token for user!
class TokenForUserMixin:
    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh)
