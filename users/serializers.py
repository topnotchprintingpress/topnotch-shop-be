from dj_rest_auth.serializers import PasswordResetSerializer
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()


class CustomPasswordResetSerializer(PasswordResetSerializer):
    def get_email_options(self):

        return {
            'email_template_name': 'password_reset_email.html'
        }
