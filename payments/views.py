from django.db import IntegrityError
import razorpay
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Payment
from doctor.models import Appointment
from django.utils.timezone import now

@csrf_exempt
@login_required(login_url="login")
def create_payment(request, appointment_id):
    client = razorpay.Client(auth=(settings.KEYID, settings.KEYSECRET))

    # Get the appointment object
    appointment = get_object_or_404(Appointment, id=appointment_id)
    amount = appointment.doctor.consultation_fee * 100  # Convert INR to paise
    # Create Razorpay order
    order = client.order.create({
        "amount": amount, 
        "currency": "INR", 
        "payment_capture": 1  
    })

    # Save the order ID in the database
    Payment.objects.create(
        appointment=appointment,
        order_id=order['id'],
        amount=amount / 100,  # Store in INR
        status="pending"  # Default status
    )

    return render(request, 'payment/razorpay_checkout.html', {
        'appointment': appointment,
        'razorpay_order_id': order['id'],
        'amount': amount / 100,
        'payment_type': "Online"
    })

@csrf_exempt
@login_required(login_url="login")
def process_payment(request, appointment_id):
    if request.method == 'POST':
        razorpay_payment_id = request.POST.get('razorpay_payment_id', None)
        razorpay_signature = request.POST.get('razorpay_signature', None)
        razorpay_order_id = request.POST.get('order_id', None)

        if not razorpay_order_id:
            return JsonResponse({'error': 'Missing order_id in request'}, status=400)

        client = razorpay.Client(auth=(settings.KEYID, settings.KEYSECRET))
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            # Verify payment signature
            client.utility.verify_payment_signature(params_dict)

            # Fetch the payment record
            payment = get_object_or_404(Payment, order_id=razorpay_order_id)
            payment.payment_id = razorpay_payment_id
            payment.status = "paid"
            payment.save()

            # Mark appointment as paid
            appointment = payment.appointment
            appointment.payment_status = "VALID"
            appointment.save()

            return redirect('payments:payment_success', appointment_id=appointment.id)

        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'error': 'Payment verification failed'}, status=400)

    return redirect('payments:payment_failure')


@csrf_exempt
@login_required(login_url="login")
def payment_success(request, appointment_id):
    return render(request, "payment/payment_success.html", {"appointment_id": appointment_id})

@csrf_exempt
@login_required(login_url="login")
def payment_failure(request):
    return render(request, "payment/payment_failure.html")