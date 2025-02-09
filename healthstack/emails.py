import os
import requests

api_key = os.getenv("ZEPTO_MAIL_API_KEY")  # Directly fetch from environment
url = os.getenv("ZEPTO_MAIL_URL")
def send_zeptomail(subject, to_email, message):
    url = url
    headers = {
        "Authorization": f"Zoho-enczapikey {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "from": {"address": "noreply@uhtarticea.com", "name": "HealXCare"},
        "to": [{"email_address": {"address": to_email}}],
        "subject": subject,
        "htmlbody": message,
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def send_zeptomail_using_template(to_email, template_token, template_data):
    """
    Sends an email using a ZeptoMail portal template.

    :param to_email: Recipient's email address
    :param template_token: Unique token of the ZeptoMail template
    :param template_data: Dictionary of dynamic variables for the template
    """
    url = "https://api.zeptomail.in/v1.1/email/template"

    headers = {
        "Authorization": f"Zoho-enczapikey {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "from": {"address": "noreply@uhtarticea.com", "name": "HealXCare"},
        "to": [{"email_address": {"address": to_email}}],
        "mail_template_key":"2518b.53e56cd38bd377f6.k1.bef12a20-e538-11ef-ac6f-525400ab18e6.194dfcff5c2",
        "merge_info": template_data

    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()  # Return ZeptoMail response
