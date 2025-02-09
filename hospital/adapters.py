import random
import string
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect
from django.contrib import messages
from healthstack.emails import send_zeptomail_using_template
from hospital.models import User, Patient
from doctor.models import Doctor_Information  # Import Doctor model
import logging

logger = logging.getLogger(__name__)

class MySocialAccountAdapter(DefaultSocialAccountAdapter):

    def generate_random_username(self, first_name):
        """ Generate a random username based on the user's first name. """
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        return f"{first_name.lower()}{random_suffix}"

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

            if login_type == "patient":
                user.is_patient = True
                user.save()

                # ✅ Create Patient profile if it doesn't exist
                if not Patient.objects.filter(user=user).exists():
                    Patient.objects.create(user=user, name=user.first_name)

                # ✅ Send welcome email
                template_token = "2518b.53e56cd38bd377f6.k1.bef12a20-e538-11ef-ac6f-525400ab18e6.194dfcff5c2"
                template_data = {"Username": user.first_name}
                send_zeptomail_using_template(user.email, template_token, template_data)

                return redirect("patient-dashboard")  # ✅ Redirect new patients

            elif login_type == "doctor":
                user.is_doctor = True
                user.save()

                # ✅ Create Doctor profile if it doesn't exist
                if not Doctor_Information.objects.filter(user=user).exists():
                    Doctor_Information.objects.create(user=user, name=user.first_name)

                # ✅ Send welcome email
                template_token = "2518b.53e56cd38bd377f6.k1.bef12a20-e538-11ef-ac6f-525400ab18e6.194dfcff5c2"
                template_data = {"Username": user.first_name}
                send_zeptomail_using_template(user.email, template_token, template_data)

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
                if not patient.name or not patient.phone_number:
                    return "/profile-settings/"  # Redirect to profile settings page
                return "/patient-dashboard/"
            elif user.is_doctor:
                return "/doctor/doctor-dashboard/"
        
        # Default redirect URL
        return "/"
        