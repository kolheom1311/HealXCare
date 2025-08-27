# import os
# import requests

# api_key = os.getenv("ZEPTO_MAIL_API_KEY")  # Directly fetch from environment
# url = os.getenv("ZEPTO_MAIL_URL")
# def send_zeptomail(subject, to_email, message):
#     url = url
#     headers = {
#         "Authorization": f"Zoho-enczapikey {api_key}",
#         "Content-Type": "application/json",
#     }

#     payload = {
#         "from": {"address": "noreply@uhtarticea.com", "name": "HealXCare"},
#         "to": [{"email_address": {"address": to_email}}],
#         "subject": subject,
#         "htmlbody": message,
#     }

#     response = requests.post(url, headers=headers, json=payload)
#     return response.json()

# def send_zeptomail_using_template(to_email, template_token, template_data):
#     """
#     Sends an email using a ZeptoMail portal template.

#     :param to_email: Recipient's email address
#     :param template_token: Unique token of the ZeptoMail template
#     :param template_data: Dictionary of dynamic variables for the template
#     """
#     url = "https://api.zeptomail.in/v1.1/email/template"

#     headers = {
#         "Authorization": f"Zoho-enczapikey {api_key}",
#         "Content-Type": "application/json",
#     }

#     payload = {
#         "from": {"address": "noreply@uhtarticea.com", "name": "HealXCare"},
#         "to": [{"email_address": {"address": to_email}}],
#         "mail_template_key":template_token,
#         "merge_info": template_data

#     }

#     response = requests.post(url, headers=headers, json=payload)
#     return response.json()  # Return ZeptoMail response


# healxcare/emails.py
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.utils.html import strip_tags
from django.conf import settings
import uuid


def send_gmail(subject, to_email, html_message):
    """
    Simple HTML mail via Gmail.
    """
    text_fallback = strip_tags(html_message) or "This email requires HTML support."
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_fallback,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    msg.attach_alternative(html_message, "text/html")
    sent = msg.send(fail_silently=False)
    return {
        "provider": "gmail",
        "status": "sent" if sent else "failed",
        "sent_count": sent,
        "to": to_email,
        "subject": subject,
        "message_id": str(uuid.uuid4()),
    }


def send_zeptomail_using_template(to_email, template_token, template_data):
    """
    Backward-compatible function that *used to* call Zepto,
    now renders Django templates from {project-root}/templates/email
    and sends via Gmail.

    Args:
        to_email (str): recipient
        template_token (str): maps to file 'email/{template_token}.html'
        template_data (dict): variables for the template (may include 'subject')
    """
    template_name = f"email/{template_token}.html"
    subject = template_data.get("subject")

    try:
        html = render_to_string(template_name, template_data)
    except TemplateDoesNotExist:
        return {
            "provider": "gmail",
            "status": "error",
            "error": "template_not_found",
            "template": template_name,
            "hint": "Ensure the file exists at {project-root}/templates/email/",
        }
    except Exception as e:
        return {
            "provider": "gmail",
            "status": "error",
            "error": str(e),
            "template": template_name,
        }

    text_fallback = strip_tags(html) or "This email requires HTML support."
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_fallback,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    msg.attach_alternative(html, "text/html")
    sent = msg.send(fail_silently=False)

    print(f"[MAIL DEBUG] Welcome mail sent={sent}, to={to_email}, subject={subject}, template={template_name}")

    return {
        "provider": "gmail",
        "status": "sent" if sent else "failed",
        "sent_count": sent,
        "to": to_email,
        "subject": subject,
        "template": template_name,
        "message_id": str(uuid.uuid4()),
    }
