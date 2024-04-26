"""
This module contains utility functions for the accounts app.
Funtions like detect_user, send_verification_email, send_notification are defined here.
"""
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage



def detect_user(user):
    """
    Determines the redirect URL based on the user's role.

    Args:
        user: An instance of the User model.

    Returns:
        str: The redirect URL based on the user's role.

    """
    if user.role == 1:
        redirecturl = "vendorDashboard"
        return redirecturl
    if user.role == 2:
        redirecturl = "custDashboard"
        return redirecturl
    if user.role is None and user.is_superadmin:
        redirecturl = "/admin"
        return redirecturl


def send_verification_email(request, user, mail_subject, email_template):
    """
    Sends a verification email to the user.

    Args:
        request (HttpRequest): The HTTP request object.
        user (User): The user object.
        mail_subject (str): The subject of the email.
        email_template (str): The path to the email template.

    Returns:
        None
    """
    from_email = "andecoreing@gmail.com"
    current_site = get_current_site(request)
    message = render_to_string(
        email_template,
        {
            "user": user,
            "domain": current_site,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": default_token_generator.make_token(user),
        },
    )
    to_email = user.email
    mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
    mail.content_subtype = "html"
    mail.send()


def send_notification(mail_subject, mail_template, context):
    """
    Sends a notification email.

    Args:
        mail_subject (str): The subject of the email.
        mail_template (str): The path to the email template.
        context (dict): The context data to be rendered in the email template.

    Returns:
        None
    """
    from_email = "andecoreing@gmail.com"
    message = render_to_string(mail_template, context)

    if isinstance(context["to_email"], str):
        to_email = []
        to_email.append(context["to_email"])
    else:
        to_email = context["to_email"]
    mail = EmailMessage(mail_subject, message, from_email, to=to_email)
    mail.content_subtype = "html"
    mail.send()
