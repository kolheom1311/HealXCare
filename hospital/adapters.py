import random
import string
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect
from django.contrib import messages
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
        """ Runs before social login. Checks if user exists and assigns roles. """
        user = sociallogin.user

        # Check if the email is provided
        if not user.email:
            messages.error(request, "Email not provided by Google.")
            return redirect("login")

        try:
            # If the user exists, log them in
            existing_user = User.objects.get(email=user.email)
            sociallogin.connect(request, existing_user)
        except User.DoesNotExist:
            # Assign roles for new users based on login_type
            login_type = request.session.get("login_type")
            user.username = self.generate_random_username(user.first_name)  # Set random username
            if login_type == "patient":
                user.is_patient = True
                # MySocialAccountAdapter.get_login_redirect_url(self,request)
                user.save()
                redirect("profile-settings")

                # Check if a Patient instance already exists for the user
                if not Patient.objects.filter(user=user).exists():
                    Patient.objects.create(user=user, name=user.first_name)  # Create patient profile
            elif login_type == "doctor":

                user.is_doctor = True
                # MySocialAccountAdapter.get_login_redirect_url(self,request)                
                user.save()
                redirect("profile-settings")


                # Check if a Doctor_Information instance already exists for the user
                if not Doctor_Information.objects.filter(user=user).exists():
                    Doctor_Information.objects.create(user=user, name=user.first_name)  # Create doctor profile
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
                return "/doctor-dashboard/"
        
        # Default redirect URL
        return "/"
        