from django import forms
from django.conf import settings

from biostar.apps.users.models import User

from captcha.fields import ReCaptchaField


class LoginForm(forms.Form):
    """
    User login form
    """
    email = forms.CharField(label='Email')
    password = forms.CharField(label='Password')

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        user = User.objects.filter(email=email).first()
        if not user:
            raise forms.ValidationError("Email not found.")
        if not user.check_password(password):
            raise forms.ValidationError("Incorrect password.")

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        if settings.USE_CAPTCHA:
            self.fields['captcha'] = ReCaptchaField()