from multiprocessing import context
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import CustomUserCreationForm, PasswordResetForm, PaymentForm
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from hospital.models import Hospital_Information, User, Patient
from doctor.models import Test, testCart, testOrder, Appointment
from hospital_admin.models import hospital_department, specialization, service, Test_Information
from django.views.decorators.cache import cache_control
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import *
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.template.loader import get_template
from xhtml2pdf import pisa
from .utils import searchDoctors, searchHospitals, searchDepartmentDoctors, paginateHospitals
from .models import Patient, User
from doctor.models import *
# from doctor.models import Doctor_Information, Appointment,Report, Specimen, Test, Prescription, Prescription_medicine, Prescription_test
from django.db.models import Q
from io import BytesIO
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from healthstack.emails import *  # Import the ZeptoMail function
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from hospital.adapters import MySocialAccountAdapter, send_zeptomail_using_template
from django.contrib.sites.shortcuts import get_current_site
import razorpay
from razorpay import Payment
import os

def send_test_email(request):
    """View to send a welcome email using ZeptoMail"""
    response = send_zeptomail(
        subject="Welcome to HealxCare - Your Journey to Better Health Starts Here!",
        to_email="rohandhonde36@gmail.com",
        message="""
        <html>
        <body>
            <h1 style="color:#2D89EF;">Welcome to HealxCare! 🎉</h1>
            <p>Dear User,</p>
            <p>We're thrilled to have you on board. Your health and well-being are our top priorities, and we’re here to support you every step of the way.</p>
            <p>With <strong>HealxCare</strong>, you can:</p>
            <ul>
                <li>✅ Access personalized health insights</li>
                <li>✅ Track your wellness progress</li>
                <li>✅ Connect with expert healthcare professionals</li>
                <li>✅ Get real-time health updates and recommendations</li>
            </ul>
            <p>To get started, simply log in to your account and explore everything we have to offer.</p>
            <p><a href="https://healxcare.in/login" style="background-color:#2D89EF;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;">Login to Your Account</a></p>
            <p>If you have any questions, our support team is always here to help.</p>
            <p>Stay healthy, stay happy.</p>
            <p><strong>The HealxCare Team</strong></p>
            <hr>
            <p>📧 Need help? Contact us at <a href="mailto:support@healxcare.com">support@healxcare.com</a></p>
        </body>
        </html>
        """
    )

    
    return JsonResponse(response)  # Return ZeptoMail response as JSON

# def send_template_email(request):
#     """View to send an email using a ZeptoMail template."""
    
#     # Unique token from ZeptoMail portal
#     template_token = "2518b.53e56cd38bd377f6.k1.bef12a20-e538-11ef-ac6f-525400ab18e6.194dfcff5c2"

#     # Dynamic variables to pass (must match ZeptoMail template placeholders)
#     template_data = {
#         "Username": "Om"
#     }

#     response = send_zeptomail_using_template(
#         to_email="kolheom1311@gmail.com",
#         template_token=template_token,
#         template_data=template_data
#     )

#     return JsonResponse(response, safe=False)

@csrf_exempt
def hospital_home(request):
    # .order_by('-created_at')[:6]
    doctors = Doctor_Information.objects.filter(register_status='Accepted')
    hospitals = Hospital_Information.objects.all()
    context = {'doctors': doctors, 'hospitals': hospitals} 
    return render(request, 'index-2.html', context)

@csrf_exempt
@login_required(login_url="login")
def change_password(request,pk):
    patient = Patient.objects.get(user_id=pk)
    context={"patient":patient}
    if request.method == "POST":
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]
        if new_password == confirm_password:
            
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request,"Password Changed Successfully")
            return redirect("patient-dashboard")
        else:
            messages.error(request,"New Password and Confirm Password is not same")
            return redirect("change-password",pk)
    return render(request, 'change-password.html',context)

def send_patient_verification_email(request, user):
    current_site = get_current_site(request)
    token_generator = PasswordResetTokenGenerator()

    verification_link = f"http://{current_site.domain}/activate/{urlsafe_base64_encode(force_bytes(user.pk))}/{token_generator.make_token(user)}/"

    template_token = "2518b.53e56cd38bd377f6.k1.5c196c50-e6af-11ef-a543-cabf48e1bf81.194e9670795"
    template_data = {
        "Link": verification_link
    }

    send_zeptomail_using_template(
        to_email=user.email,
        template_token=template_token,
        template_data=template_data
    )

def add_billing(request):
    return render(request, 'add-billing.html')

def appointments(request):
    return render(request, 'appointments.html')

def edit_billing(request):
    return render(request, 'edit-billing.html')

def edit_prescription(request):
    return render(request, 'edit-prescription.html')

@csrf_exempt
def resetPassword(request):
    form = PasswordResetForm()

    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            # Check if user exists before proceeding
            user = User.objects.filter(email=email).first()
            if not user:
                messages.error(request, 'No user found with this email address.')
                return redirect('reset_password')

            current_site = get_current_site(request)
            token_generator = PasswordResetTokenGenerator()
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = token_generator.make_token(user)

            # Construct Password Reset Link
            reset_link = f"http://{current_site.domain}/reset/{uid}/{token}/"

            # **ZeptoMail Integration**
            template_token = "2518b.53e56cd38bd377f6.k1.4c77b750-e6e8-11ef-ab60-525400b0b0f3.194eadc2f45"
            template_data = {
                "reset-link": reset_link
            }

            send_zeptomail_using_template(
                to_email=user.email,
                template_token=template_token,
                template_data=template_data
            )

            messages.success(request, 'Password reset link sent to your email.')
            return redirect("password_reset_done")

    context = {'form': form}
    return render(request, 'reset_password.html', context)
   
    
def privacy_policy(request):
    return render(request, 'privacy-policy.html')

def about_us(request):
    return render(request, 'about-us.html')

def Health_Advice(request):
    patient = None
    if request.user.is_authenticated and hasattr(request.user, 'patient'):
        patient = request.user.patient

    return render(request, 'HealthAdvice.html', {"patient": patient})

@csrf_exempt
@login_required(login_url="login")
def chat(request, pk):
    patient = Patient.objects.get(user_id=pk)
    doctors = Doctor_Information.objects.all()

    context = {'patient': patient, 'doctors': doctors}
    return render(request, 'chat.html', context)

@csrf_exempt
@login_required(login_url="login")
def doctor_profile(request, pk):
    # request.user --> get logged in user
    if request.user.is_patient:
        patient = request.user.patient
    else:
        patient = None
    
    doctor = Doctor_Information.objects.get(doctor_id=pk)
    # doctor = Doctor_Information.objects.filter(doctor_id=pk).order_by('-doctor_id')
    
    educations = Education.objects.filter(doctor=doctor).order_by('-year_of_completion')
    experiences = Experience.objects.filter(doctor=doctor).order_by('-from_year','-to_year')
    doctor_review = Doctor_review.objects.filter(doctor=doctor)
            
    context = {'doctor': doctor, 'patient': patient, 'educations': educations, 'experiences': experiences, 'doctor_review': doctor_review}
    return render(request, 'doctor-profile.html', context)


@csrf_exempt
@login_required(login_url="login")
def chat_doctor(request):
    if request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        patients = Patient.objects.all()
        
    context = {'patients': patients, 'doctor': doctor}
    return render(request, 'chat-doctor.html', context)

@csrf_exempt     
@login_required(login_url="login")
def pharmacy_shop(request):
    return render(request, 'pharmacy/shop.html')

'''
@csrf_exempt
def login_user(request):
    page = 'patient_login'
    if request.method == 'GET':
        return render(request, 'patient-login.html')
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            if request.user.is_patient:   
                messages.success(request, 'User Logged in Successfully')    
                return redirect('patient-dashboard')
            else:
                messages.error(request, 'Invalid credentials. Not a Patient')
                return redirect('logout')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'patient-login.html')
'''

@csrf_exempt
def login_user(request):
    request.session["login_type"] = "patient"  # Set login type for patients
    page = 'patient_login'
    if request.method == 'GET':
        return render(request, 'patient-login.html')
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'Username does not exist')
            return render(request, 'patient-login.html')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_patient:  # Check if the user is a patient
                try:
                    patient = user.patient  # Access the related Patient model
                except Patient.DoesNotExist:
                    messages.error(request, 'Patient profile not found.')
                    return redirect('logout')

                # Check if name or phone_number is blank
                if not patient.name or not patient.phone_number:
                    messages.warning(request, 'Please complete your profile settings.')
                    return redirect('profile-settings')  # Redirect to profile settings page

                messages.success(request, 'User logged in successfully')
                return redirect('patient-dashboard')
            else:
                messages.error(request, 'Invalid credentials. Not a Patient')
                return redirect('logout')
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, 'patient-login.html')

    return render(request, 'patient-login.html')

@csrf_exempt
def redirect_after_google_login(request):
    redirect_url = MySocialAccountAdapter().get_login_redirect_url(request)
    return redirect(redirect_url)  # Redirecting to the determined URL

@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logoutUser(request):
    logout(request)
    messages.success(request, 'User Logged out')
    return redirect('login')

@csrf_exempt
# def patient_register(request):
#     page = 'patient-register'
#     form = CustomUserCreationForm()

#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)  # Don't save yet to modify
#             user.is_patient = True
#             user.save()

#             # Fallback if user's name is empty
#             username = user.username # if user.username.strip() else "User"
#             # Send email after successful registration
#             template_token = "2518b.53e56cd38bd377f6.k1.bef12a20-e538-11ef-ac6f-525400ab18e6.194dfcff5c2"
#             template_data = {
#                 "Username": username  # Use first name or fallback
#             }
            
#             send_zeptomail_using_template(
#                 to_email=user.email,  # Send email to registered user
#                 template_token=template_token,
#                 template_data=template_data
#             )

#             messages.success(request, 'Patient account was created! A confirmation email has been sent.')

#             return redirect('login')
#         else:
#             messages.error(request, 'An error has occurred during registration')

#     context = {'page': page, 'form': form}
#     return render(request, 'patient-register.html', context)
def patient_register(request):
    page = 'patient-register'
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Don't save yet to modify
            user.is_patient = True
            user.is_active = False  # Mark as inactive until verification
            user.save()

            # Generate verification email
            send_patient_verification_email(request, user)

            messages.success(request, 'Patient account was created! A confirmation email has been sent.')
            return redirect('login')
        else:
            messages.error(request, 'An error has occurred during registration')

    context = {'page': page, 'form': form}
    return render(request, 'patient-register.html', context)


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None:
        token_generator = PasswordResetTokenGenerator()
        token_valid = token_generator.check_token(user, token)
        
        # Check if the token is still valid
        if token_valid:
            user.is_active = True
            user.save()
            messages.success(request, 'Your account has been verified! You can now log in.')
            
        
            # Fallback if user's name is empty
            username = user.username # if user.username.strip() else "User"
            # Send email after successful registration
            template_token = "2518b.53e56cd38bd377f6.k1.bef12a20-e538-11ef-ac6f-525400ab18e6.194dfcff5c2"
            template_data = {
                "Username": username  # Use first name or fallback
            }
            
            send_zeptomail_using_template(
                to_email=user.email,  # Send email to registered user
                template_token=template_token,
                template_data=template_data
            )

            return redirect('login')
        

        else:
            messages.error(request, 'Activation link is invalid or expired.')
            return redirect('patient-register')

    messages.error(request, 'Activation link is invalid or expired.')
    return redirect('patient-register')


@csrf_exempt
@login_required(login_url="login")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def patient_dashboard(request):
    if request.user.is_patient:
        # patient = Patient.objects.get(user_id=pk)
        patient = Patient.objects.get(user=request.user)
        report = Report.objects.filter(patient=patient)
        prescription = Prescription.objects.filter(patient=patient).order_by('-prescription_id')
        appointments = Appointment.objects.filter(patient=patient).filter(Q(appointment_status='pending') | Q(appointment_status='confirmed'))
        # payments = Payment.objects.filter(patient=patient).filter(appointment__in=appointments).filter(payment_type='appointment').filter(status='VALID')
        # context = {'patient': patient, 'appointments': appointments, 'payments': payments,'report':report,'prescription':prescription}
        context = {'patient': patient, 'appointments': appointments,'report':report,'prescription':prescription}
    else:
        return redirect('logout')
        
    return render(request, 'patient-dashboard.html', context)

@csrf_exempt
@login_required(login_url="login")
def profile_settings(request):
    if request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        old_featured_image = patient.featured_image

        if request.method == 'GET':
            context = {'patient': patient}
            return render(request, 'profile-settings.html', context)
        
        elif request.method == 'POST':
            featured_image = request.FILES.get('featured_image', old_featured_image)
            name = request.POST.get('name')
            dob = request.POST.get('dob')
            age = request.POST.get('age')
            blood_group = request.POST.get('blood_group')
            phone_number = request.POST.get('phone_number')
            address = request.POST.get('address')
            nid = request.POST.get('nid')
            history = request.POST.get('history')

            # Validate required fields
            required_fields = [name, dob, age, phone_number, address]
            if all(required_fields):
                patient.name = name
                patient.age = age
                patient.phone_number = phone_number
                patient.address = address
                patient.blood_group = blood_group
                patient.history = history
                patient.dob = dob
                patient.nid = nid
                patient.featured_image = featured_image
                patient.profile_completed = True
                patient.save()
                messages.success(request, 'Profile updated successfully!')
            else:
                messages.error(request, 'Please fill in all required fields.')
                return redirect('profile-settings')
            
            return redirect('patient-dashboard')
    else:
        return redirect('logout')
    
@csrf_exempt
@login_required(login_url="login")
def search(request):
    if request.user.is_authenticated and request.user.is_patient:
        # patient = Patient.objects.get(user_id=pk)
        patient = Patient.objects.get(user=request.user)
        doctors = Doctor_Information.objects.filter(register_status='Accepted')
        
        doctors, search_query = searchDoctors(request)
        context = {'patient': patient, 'doctors': doctors, 'search_query': search_query}
        return render(request, 'search.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')    
    
@csrf_exempt
@login_required(login_url="login")
def multiple_hospital(request):
    
    if request.user.is_authenticated: 
        
        if request.user.is_patient:
            # patient = Patient.objects.get(user_id=pk)
            patient = Patient.objects.get(user=request.user)
            doctors = Doctor_Information.objects.all()
            hospitals = Hospital_Information.objects.all()
            
            hospitals, search_query = searchHospitals(request)
            
            # PAGINATION ADDED TO MULTIPLE HOSPITALS
            custom_range, hospitals = paginateHospitals(request, hospitals, 3)
        
            context = {'patient': patient, 'doctors': doctors, 'hospitals': hospitals, 'search_query': search_query, 'custom_range': custom_range}
            return render(request, 'multiple-hospital.html', context)
        
        elif request.user.is_doctor:
            doctor = Doctor_Information.objects.get(user=request.user)
            hospitals = Hospital_Information.objects.all()
            
            hospitals, search_query = searchHospitals(request)
            
            context = {'doctor': doctor, 'hospitals': hospitals, 'search_query': search_query}
            return render(request, 'multiple-hospital.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html') 
    
@csrf_exempt    
@login_required(login_url="login")
def hospital_profile(request, pk):
    
    if request.user.is_authenticated: 
        
        if request.user.is_patient:
            patient = Patient.objects.get(user=request.user)
            doctors = Doctor_Information.objects.all()
            hospitals = Hospital_Information.objects.get(hospital_id=pk)
        
            departments = hospital_department.objects.filter(hospital=hospitals)
            specializations = specialization.objects.filter(hospital=hospitals)
            services = service.objects.filter(hospital=hospitals)
            
            # department_list = None
            # for d in departments:
            #     vald = d.hospital_department_name
            #     vald = re.sub("'", "", vald)
            #     vald = vald.replace("[", "")
            #     vald = vald.replace("]", "")
            #     vald = vald.replace(",", "")
            #     department_list = vald.split()
            
            context = {'patient': patient, 'doctors': doctors, 'hospitals': hospitals, 'departments': departments, 'specializations': specializations, 'services': services}
            return render(request, 'hospital-profile.html', context)
        
        elif request.user.is_doctor:
           
            doctor = Doctor_Information.objects.get(user=request.user)
            hospitals = Hospital_Information.objects.get(hospital_id=pk)
            
            departments = hospital_department.objects.filter(hospital=hospitals)
            specializations = specialization.objects.filter(hospital=hospitals)
            services = service.objects.filter(hospital=hospitals)
            
            context = {'doctor': doctor, 'hospitals': hospitals, 'departments': departments, 'specializations': specializations, 'services': services}
            return render(request, 'hospital-profile.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html') 
    
def data_table(request):
    return render(request, 'data-table.html')

@csrf_exempt
@login_required(login_url="login")
def hospital_department_list(request, pk):
    if request.user.is_authenticated: 
        
        if request.user.is_patient:
            # patient = Patient.objects.get(user_id=pk)
            patient = Patient.objects.get(user=request.user)
            doctors = Doctor_Information.objects.all()
            
            hospitals = Hospital_Information.objects.get(hospital_id=pk)
            departments = hospital_department.objects.filter(hospital=hospitals)
        
            context = {'patient': patient, 'doctors': doctors, 'hospitals': hospitals, 'departments': departments}
            return render(request, 'hospital-department.html', context)
        
        elif request.user.is_doctor:
            doctor = Doctor_Information.objects.get(user=request.user)
            hospitals = Hospital_Information.objects.get(hospital_id=pk)
            departments = hospital_department.objects.filter(hospital=hospitals)
            
            context = {'doctor': doctor, 'hospitals': hospitals, 'departments': departments}
            return render(request, 'hospital-department.html', context)
    else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'patient-login.html')

@csrf_exempt
@login_required(login_url="login")
def hospital_doctor_list(request, pk):
    if request.user.is_authenticated and request.user.is_patient:
        # patient = Patient.objects.get(user_id=pk)
        patient = Patient.objects.get(user=request.user)
        departments = hospital_department.objects.get(hospital_department_id=pk)
        doctors = Doctor_Information.objects.filter(department_name=departments)
        
        doctors, search_query = searchDepartmentDoctors(request, pk)
        
        context = {'patient': patient, 'department': departments, 'doctors': doctors, 'search_query': search_query, 'pk_id': pk}
        return render(request, 'hospital-doctor-list.html', context)

    elif request.user.is_authenticated and request.user.is_doctor:
        # patient = Patient.objects.get(user_id=pk)
        
        doctor = Doctor_Information.objects.get(user=request.user)
        departments = hospital_department.objects.get(hospital_department_id=pk)
        
        doctors = Doctor_Information.objects.filter(department_name=departments)
        doctors, search_query = searchDepartmentDoctors(request, pk)
        
        context = {'doctor':doctor, 'department': departments, 'doctors': doctors, 'search_query': search_query, 'pk_id': pk}
        return render(request, 'hospital-doctor-list.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')   
    
@csrf_exempt
@login_required(login_url="login")
def hospital_doctor_register(request, pk):
    if request.user.is_authenticated: 
        
        if request.user.is_doctor:
            doctor = Doctor_Information.objects.get(user=request.user)
            hospitals = Hospital_Information.objects.get(hospital_id=pk)
            
            departments = hospital_department.objects.filter(hospital=hospitals)
            specializations = specialization.objects.filter(hospital=hospitals)
            
            if request.method == 'POST':
                if 'certificate_image' in request.FILES:
                    certificate_image = request.FILES['certificate_image']
                else:
                    certificate_image = "doctors_certificate/default.png"
                
                department_id_selected = request.POST.get('department_radio')
                specialization_id_selected = request.POST.get('specialization_radio')
                
                department_chosen = hospital_department.objects.get(hospital_department_id=department_id_selected)
                specialization_chosen = specialization.objects.get(specialization_id=specialization_id_selected)
                
                doctor.department_name = department_chosen
                doctor.specialization = specialization_chosen
                doctor.register_status = 'Pending'
                doctor.certificate_image = certificate_image
                
                doctor.save()
                
                messages.success(request, 'Hospital Registration Request Sent')
                
                return redirect('doctor-dashboard')
                
                 
            context = {'doctor': doctor, 'hospitals': hospitals, 'departments': departments, 'specializations': specializations}
            return render(request, 'hospital-doctor-register.html', context)
    else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'doctor-login.html')
   
def testing(request):
    # hospitals = Hospital_Information.objects.get(hospital_id=1)
    test = "test"
    context = {'test': test}
    return render(request, 'testing.html', context)

@csrf_exempt
@login_required(login_url="login")
def view_report(request,pk):
    if request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        report = Report.objects.filter(report_id=pk)
        specimen = Specimen.objects.filter(report__in=report)
        test = Test.objects.filter(report__in=report)

        # current_date = datetime.date.today()
        context = {'patient':patient,'report':report,'test':test,'specimen':specimen}
        return render(request, 'view-report.html',context)
    else:
        redirect('logout') 


def test_cart(request):
    return render(request, 'test-cart.html')

@csrf_exempt
@login_required(login_url="login")
def test_single(request,pk):
     if request.user.is_authenticated and request.user.is_patient:
         
        patient = Patient.objects.get(user=request.user)
        Perscription_test = Perscription_test.objects.get(test_id=pk)
        carts = testCart.objects.filter(user=request.user, purchased=False)
        
        context = {'patient': patient, 'carts': carts, 'Perscription_test': Perscription_test}
        return render(request, 'test-cart.html',context)
     else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'patient-login.html')  

@csrf_exempt
@login_required(login_url="login")
def test_add_to_cart(request, pk, pk2):
    if request.user.is_authenticated and request.user.is_patient:
         
        patient = Patient.objects.get(user=request.user)
        test_information = Test_Information.objects.get(test_id=pk2)
        prescription = Prescription.objects.filter(prescription_id=pk)

        item = get_object_or_404(Prescription_test, test_info_id=pk2,prescription_id=pk)
        order_item = testCart.objects.get_or_create(item=item, user=request.user, purchased=False)
        order_qs = testOrder.objects.filter(user=request.user, ordered=False)

        if order_qs.exists():
            order = order_qs[0]
            order.orderitems.add(order_item[0])
            # messages.info(request, "This test is added to your cart!")
            return redirect("prescription-view", pk=pk)
        else:
            order = testOrder(user=request.user)
            order.save()
            order.orderitems.add(order_item[0])
            return redirect("prescription-view", pk=pk)

        context = {'patient': patient,'prescription_test': prescription_tests,'prescription':prescription,'prescription_medicine':prescription_medicine,'test_information':test_information}
        return render(request, 'prescription-view.html', context)
    else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'patient-login.html')  

@csrf_exempt
@login_required(login_url="login")
def test_cart(request, pk):
    if request.user.is_authenticated and request.user.is_patient:
        # prescription = Prescription.objects.filter(prescription_id=pk)
        
        prescription = Prescription.objects.filter(prescription_id=pk)
        
        patient = Patient.objects.get(user=request.user)
        prescription_test = Prescription_test.objects.all()
        test_carts = testCart.objects.filter(user=request.user, purchased=False)
        test_orders = testOrder.objects.filter(user=request.user, ordered=False)
        
        if test_carts.exists() and test_orders.exists():
            test_order = test_orders[0]
            
            context = {'test_carts': test_carts,'test_order': test_order, 'patient': patient, 'prescription_test':prescription_test, 'prescription_id':pk}
            return render(request, 'test-cart.html', context)
        else:
            # messages.warning(request, "You don't have any test in your cart!")
            context = {'patient': patient,'prescription_test':prescription_test}
            return render(request, 'prescription-view.html', context)
    else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'patient-login.html') 

@csrf_exempt
@login_required(login_url="login")
def test_remove_cart(request, pk):
    if request.user.is_authenticated and request.user.is_patient:
        item = Prescription_test.objects.get(test_id=pk)

        patient = Patient.objects.get(user=request.user)
        prescription = Prescription.objects.filter(prescription_id=pk)
        prescription_medicine = Prescription_medicine.objects.filter(prescription__in=prescription)
        prescription_test = Prescription_test.objects.filter(prescription__in=prescription)
        test_carts = testCart.objects.filter(user=request.user, purchased=False)
        
        # item = get_object_or_404(test, pk=pk)
        test_order_qs = testOrder.objects.filter(user=request.user, ordered=False)
        if test_order_qs.exists():
            test_order = test_order_qs[0]
            if test_order.orderitems.filter(item=item).exists():
                test_order_item = testCart.objects.filter(item=item, user=request.user, purchased=False)[0]
                test_order.orderitems.remove(test_order_item)
                test_order_item.delete()
                # messages.warning(request, "This test was remove from your cart!")
                context = {'test_carts': test_carts,'test_order': test_order,'patient': patient,'prescription_id':pk}
                return render(request, 'test-cart.html', context)
            else:
                # messages.info(request, "This test was not in your cart")
                context = {'patient': patient,'test': item,'prescription':prescription,'prescription_medicine':prescription_medicine,'prescription_test':prescription_test}
                return render(request, 'prescription-view.html', context)
        else:
            # messages.info(request, "You don't have an active order")
            context = {'patient': patient,'test': item,'prescription':prescription,'prescription_medicine':prescription_medicine,'prescription_test':prescription_test}
            return redirect('prescription-view', pk=prescription.prescription_id)
    else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'patient-login.html') 

@csrf_exempt
def prescription_view(request,pk):
      if request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        prescription = Prescription.objects.filter(prescription_id=pk)
        prescription_medicine = Prescription_medicine.objects.filter(prescription__in=prescription)
        prescription_test = Prescription_test.objects.filter(prescription__in=prescription)

        context = {'patient':patient,'prescription':prescription,'prescription_test':prescription_test,'prescription_medicine':prescription_medicine}
        return render(request, 'prescription-view.html',context)
      else:
         redirect('logout') 

@csrf_exempt
def render_to_pdf(template_src, context_dict={}):
    template=get_template(template_src)
    html=template.render(context_dict)
    result=BytesIO()
    pres_pdf=pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pres_pdf.err:
        return HttpResponse(result.getvalue(),content_type="aplication/pres_pdf")
    return None


# def prescription_pdf(request,pk):
#  if request.user.is_patient:
#     patient = Patient.objects.get(user=request.user)
#     prescription = Prescription.objects.get(prescription_id=pk)
#     perscription_medicine = Perscription_medicine.objects.filter(prescription=prescription)
#     perscription_test = Perscription_test.objects.filter(prescription=prescription)
#     current_date = datetime.date.today()
#     context={'patient':patient,'current_date' : current_date,'prescription':prescription,'perscription_test':perscription_test,'perscription_medicine':perscription_medicine}
#     pdf=render_to_pdf('prescription_pdf.html', context)
#     if pdf:
#         response=HttpResponse(pdf, content_type='application/pdf')
#         content="inline; filename=report.pdf"
#         # response['Content-Disposition']= content
#         return response
#     return HttpResponse("Not Found")

@csrf_exempt
def prescription_pdf(request,pk):
 if request.user.is_patient:
    patient = Patient.objects.get(user=request.user)
    prescription = Prescription.objects.get(prescription_id=pk)
    prescription_medicine = Prescription_medicine.objects.filter(prescription=prescription)
    prescription_test = Prescription_test.objects.filter(prescription=prescription)
    # current_date = datetime.date.today()
    context={'patient':patient,'prescription':prescription,'prescription_test':prescription_test,'prescription_medicine':prescription_medicine}
    pres_pdf=render_to_pdf('prescription_pdf.html', context)
    if pres_pdf:
        response=HttpResponse(pres_pdf, content_type='application/pres_pdf')
        content="inline; filename=prescription.pdf"
        response['Content-Disposition']= content
        return response
    return HttpResponse("Not Found")

@csrf_exempt
@login_required(login_url="login")
def delete_prescription(request,pk):
    if request.user.is_authenticated and request.user.is_patient:
        prescription = Prescription.objects.get(prescription_id=pk)
        prescription.delete()
        messages.success(request, 'Prescription Deleted')
        return redirect('patient-dashboard')
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')

@csrf_exempt
@login_required(login_url="login")
def delete_report(request,pk):
    if request.user.is_authenticated and request.user.is_patient:
        report = Report.objects.get(report_id=pk)
        report.delete()
        messages.success(request, 'Report Deleted')
        return redirect('patient-dashboard')
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')

@csrf_exempt
@receiver(user_logged_in)
def got_online(sender, user, request, **kwargs):    
    user.login_status = True
    user.save()

@csrf_exempt
@receiver(user_logged_out)
def got_offline(sender, user, request, **kwargs):   

    user.login_status = False
    user.save() 