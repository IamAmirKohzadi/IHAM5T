from django.test import TestCase

from accounts.forms import TemplatedPasswordResetForm
from accounts.models import User


class TestAccountForms(TestCase):
    def test_password_reset_form_valid(self):
        user = User.objects.create_user(
            email="reset@test.com",
            password="TestPass123!",
        )
        form = TemplatedPasswordResetForm(data={"email": user.email})
        self.assertTrue(form.is_valid())
