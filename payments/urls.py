from django.urls import path
from .views import create_payment, process_payment, payment_success, payment_failure

app_name = "payments"  # 👈 This enables namespacing

urlpatterns = [
    path('create/<int:appointment_id>/', create_payment, name='create_payment'),
    path('process/<int:appointment_id>/', process_payment, name='process_payment'),
    path('success/<int:appointment_id>/', payment_success, name='payment_success'),
    path('failure/', payment_failure, name='payment_failure'),
]