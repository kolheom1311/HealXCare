from django.urls import path
from .views import *

app_name = "payments"  # 👈 This enables namespacing

urlpatterns = [
    path('create/<int:appointment_id>/', create_payment, name='create_payment'),
    path('invoice/<str:payment_id>/', billing_invoice_view, name='billing_invoice'),
    path('invoice/<str:payment_id>/download/', download_invoice_view, name='download_invoice'),
    path('process/<int:appointment_id>/', process_payment, name='process_payment'),
    path('success/<int:appointment_id>/', payment_success, name='payment_success'),
    path('failure/', payment_failure, name='payment_failure'),
]