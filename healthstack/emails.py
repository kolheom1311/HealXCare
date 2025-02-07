# import requests
# import json
# from django.conf import settings

# def send_zeptomail(subject, to_email, message):
#     # url = "https://api.zeptomail.com/v1.1/email"
#     # headers = {
#     #     "Authorization": "Zoho-enczapikey PHtE6r1fF+y5i2Ero0MGsPG+RZagNN96qbluLAkU5opKW6MAHU0E+IwvxzK0o0wsV/hDF/6eyog5uLOUsO+NJ2jkYW8dWmqyqK3sx/VYSPOZsbq6x00buFgSckDVUYbndt9r0S3RutvfNA==",
#     #     "Content-Type": "application/json",
#     # }
    
#     # payload = {
#     #     "from": {
#     #         "address": "team@uhtarticea.com",
#     #         "name": "HealXCare"  # Change this to your project name
#     #     },
#     #     "to": [{"email_address": {"address": to_email}}],
#     #     "subject": subject,
#     #     "htmlbody": message,  # Supports HTML content
#     # }

#     # response = requests.post(url, headers=headers, data=json.dumps(payload))
#     # return response.json()
#     url = "https://api.zeptomail.in/v1.1/email"

#     payload = "{\n\"from\": { \"address\": \"healxcare@uhtarticea.com\"},\n\"to\": [{\"email_address\": {\"address\": \"pchaudhari2303@gmail.com\",\"name\": \"Om\"}}],\n\"subject\":\"Test Email from HealXCare\",\n\"htmlbody\":\"<div><b> Test email sent successfully.  </b></div>\"\n}"
#     headers = {
#     'accept': "application/json",
#     'content-type': "application/json",
#     'authorization': "Zoho-enczapikey PHtE6r1fF+y5i2Ero0MGsPG+RZagNN96qbluLAkU5opKW6MAHU0E+IwvxzK0o0wsV/hDF/6eyog5uLOUsO+NJ2jkYW8dWmqyqK3sx/VYSPOZsbq6x00buFgSckDVUYbndt9r0S3RutvfNA==",
#     }

#     response = requests.request("POST", url, data=payload, headers=headers)

#     print(response.text)

import os
import requests

api_key = os.getenv("ZEPTO_MAIL_API_KEY")  # Directly fetch from environment

print("DEBUG: API Key in emails.py =", api_key)  # Debugging

def send_zeptomail(subject, to_email, message):
    url = "https://api.zeptomail.in/v1.1/email"
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
