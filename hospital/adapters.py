import random
import string
import requests
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount, SocialToken
from django.shortcuts import redirect
from django.contrib import messages
from healxcare.emails import send_zeptomail_using_template
from hospital.models import User, Patient
from doctor.models import Doctor_Information  
import logging

logger = logging.getLogger(__name__)

class MySocialAccountAdapter(DefaultSocialAccountAdapter):

    def generate_random_username(self, first_name):
        """ Generate a random username based on the user's first name. """
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        return f"{first_name.lower()}{random_suffix}"

    def fetch_google_user_info(self, request, sociallogin):
        """ Fetch additional user details from Google's API. """
        try:
            social_account = SocialAccount.objects.get(user=sociallogin.user, provider="google")
            social_token = SocialToken.objects.get(account=social_account)
            access_token = social_token.token

            google_api_url = "https://people.googleapis.com/v1/people/me"
            params = {
                "personFields": "names,emailAddresses,birthdays,phoneNumbers,addresses,genders",
                "key": "YOUR_GOOGLE_API_KEY"
            }
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(google_api_url, headers=headers, params=params)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch user info: {response.text}")
                return {}

        except Exception as e:
            logger.error(f"Error fetching Google user info: {e}")
            return {}

    def pre_social_login(self, request, sociallogin):
        """Runs before social login. Checks if user exists and assigns roles."""
        user = sociallogin.user

        # ✅ Check if email is provided
        if not user.email:
            messages.error(request, "Email not provided by Google.")
            return redirect("login")

        try:
            # ✅ If the user exists, connect and log in
            existing_user = User.objects.get(email=user.email)
            sociallogin.connect(request, existing_user)
            
            # ✅ Redirect based on user type
            if existing_user.is_patient:
                return redirect("/patient-dashboard/")  
            elif existing_user.is_doctor:
                return redirect("/doctor-dashboard/")  
            else:
                return redirect("/profile-settings/")

        except User.DoesNotExist:
            # ✅ Assign roles for new users
            login_type = request.session.get("login_type")
            user.username = self.generate_random_username(user.first_name)  # Set random username

            # ✅ Extract additional user info from Google
            extra_data = sociallogin.account.extra_data
            phone_number = extra_data.get("phoneNumbers", [{}])[0].get("value", None)
            dob = extra_data.get("birthdays", [{}])[0].get("date", None)
            address = extra_data.get("addresses", [{}])[0].get("formattedValue", None)

            # ✅ Ensure phone number is stored as None if it's empty
            if not phone_number or phone_number.strip() == "":
                phone_number = None

            if login_type == "patient":
                user.is_patient = True
                user.save()

                # ✅ Create Patient profile if it doesn't exist
                if not Patient.objects.filter(user=user).exists():
                    Patient.objects.create(
                        user=user,
                        name=user.first_name,
                        phone_number=phone_number,  # Store None if empty
                        dob=dob,
                        address=address
                    )

                return redirect("patient-dashboard")  # ✅ Redirect new patients

            elif login_type == "doctor":
                user.is_doctor = True
                user.save()

                # ✅ Create Doctor profile if it doesn't exist
                if not Doctor_Information.objects.filter(user=user).exists():
                    Doctor_Information.objects.create(
                        user=user,
                        name=user.first_name,
                        phone_number=phone_number,  # Store None if empty
                        dob=dob,
                        location=address
                    )

                return redirect("doctor-dashboard")  # ✅ Redirect new doctors

            else:
                messages.error(request, "Invalid login request")
                return redirect("login")

    def get_login_redirect_url(self, request):
        """ Redirect user to the appropriate dashboard after login. """
        user = request.user

        if user.is_authenticated:
            if user.is_patient:
                patient = user.patient
                # Check if the profile is incomplete
                if not patient.profile_completed:
                    return "/profile-settings/"  # Redirect to profile settings page
                return "/patient-dashboard/"
            elif user.is_doctor:
                doctor = user.profile
                if not doctor.profile_completed:
                    return "/doctor/profile-settings/"  # Redirect to profile settings page
                return "/doctor/doctor-dashboard/"
        
        return "/"
