from io import BytesIO
from django.db import IntegrityError
import razorpay
from xhtml2pdf import pisa
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Payment
from hospital.models import Patient
from django.template.loader import get_template
from doctor.models import Appointment
from django.utils.timezone import now
import pdfkit

@csrf_exempt
@login_required(login_url="login")
def create_payment(request, appointment_id):
    client = razorpay.Client(auth=(settings.KEYID, settings.KEYSECRET))

    # Get the appointment object
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Determine amount based on appointment type
    if appointment.appointment_type == "checkup":
        amount = appointment.doctor.consultation_fee * 100  # Convert INR to paise
    else:
        amount = appointment.doctor.report_fee * 100  # Convert INR to paise

    # Check if a payment already exists for this appointment
    existing_payment = Payment.objects.filter(appointment=appointment).first()

    if existing_payment:
        if existing_payment.status in ["pending", "cancelled"]:
            # If payment is pending or cancelled, reuse the same order
            existing_payment.status = "pending"  # Reset status if it was cancelled
            existing_payment.save()
            razorpay_order_id = existing_payment.order_id
        else:
            # If the previous payment was completed, create a new order
            order = client.order.create({
                "amount": amount,
                "currency": "INR",
                "payment_capture": 1  
            })
            existing_payment.order_id = order['id']
            existing_payment.amount = amount / 100
            existing_payment.status = "pending"  # Reset status
            existing_payment.save()
            razorpay_order_id = order['id']
    else:
        # No existing payment, create a new one
        order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1  
        })
        Payment.objects.create(
            appointment=appointment,
            order_id=order['id'],
            amount=amount / 100,
            status="pending"
        )
        razorpay_order_id = order['id']

    return render(request, 'payment/razorpay_checkout.html', {
        'appointment': appointment,
        'razorpay_order_id': razorpay_order_id,
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

            # Fetch the existing payment record
            payment = get_object_or_404(Payment, order_id=razorpay_order_id)

            # Prevent duplicate updates if already marked as paid
            if payment.status == "paid":
                return redirect('payments:payment_success', appointment_id=payment.appointment.id)

            # Update payment status
            payment.payment_id = razorpay_payment_id
            payment.status = "paid"
            payment.save()

            # Update appointment payment status
            appointment = payment.appointment
            appointment.payment_status = "VALID"
            appointment.save()

            return redirect('payments:payment_success', appointment_id=appointment.id)

        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'error': 'Payment verification failed'}, status=400)

    return redirect('payments:payment_failure')

# @csrf_exempt
# @login_required(login_url="login")
# def create_payment(request, appointment_id):
#     client = razorpay.Client(auth=(settings.KEYID, settings.KEYSECRET))

#     # Get the appointment object
#     appointment = get_object_or_404(Appointment, id=appointment_id)

#     # Determine amount based on appointment type
#     if appointment.appointment_type == "checkup":
#         amount = appointment.doctor.consultation_fee * 100  # Convert INR to paise
#     else:
#         amount = appointment.doctor.report_fee * 100  # Convert INR to paise

#     # Check if a pending or failed payment exists for this appointment
#     existing_payment = Payment.objects.filter(
#         appointment=appointment, 
#         status__in=["pending", "failed"]
#     ).first()

#     if existing_payment:
#         # Reuse the existing payment order
#         razorpay_order_id = existing_payment.order_id
#         existing_payment.status = "pending"  # Ensure it is marked as pending again
#         existing_payment.save()
#     else:
#         # No existing pending/failed payment, create a new one
#         order = client.order.create({
#             "amount": amount,
#             "currency": "INR",
#             "payment_capture": 1
#         })

#         existing_payment = Payment.objects.create(
#             appointment=appointment,
#             order_id=order['id'],
#             amount=amount / 100,
#             status="pending"
#         )
#         razorpay_order_id = order['id']

#     return render(request, 'payment/razorpay_checkout.html', {
#         'appointment': appointment,
#         'razorpay_order_id': razorpay_order_id,
#         'amount': amount / 100,
#         'payment_type': "Online"
#     })

# @csrf_exempt
# @login_required(login_url="login")
# def process_payment(request, appointment_id):
#     if request.method == 'POST':
#         razorpay_payment_id = request.POST.get('razorpay_payment_id', None)
#         razorpay_signature = request.POST.get('razorpay_signature', None)
#         razorpay_order_id = request.POST.get('order_id', None)

#         if not razorpay_order_id:
#             return JsonResponse({'error': 'Missing order_id in request'}, status=400)

#         client = razorpay.Client(auth=(settings.KEYID, settings.KEYSECRET))
#         params_dict = {
#             'razorpay_order_id': razorpay_order_id,
#             'razorpay_payment_id': razorpay_payment_id,
#             'razorpay_signature': razorpay_signature
#         }

#         try:
#             # Verify payment signature
#             client.utility.verify_payment_signature(params_dict)

#             # Fetch the payment record
#             payment = get_object_or_404(Payment, order_id=razorpay_order_id)

#             # Prevent duplicate updates if already marked as paid
#             if payment.status == "paid":
#                 return redirect('payments:payment_success', appointment_id=payment.appointment.id)

#             # Update payment status
#             payment.payment_id = razorpay_payment_id
#             payment.status = "paid"
#             payment.save()

#             # Update appointment payment status
#             appointment = payment.payment_id
#             appointment.payment_status = "VALID"
#             appointment.save()

#             return redirect('payments:payment_success', appointment_id=appointment.id)

#         except razorpay.errors.SignatureVerificationError:
#             return JsonResponse({'error': 'Payment verification failed'}, status=400)

#     return redirect('payments:payment_failure')


@csrf_exempt
@login_required(login_url="login")
def payment_success(request, appointment_id):
    return render(request, "payment/payment_success.html", {"appointment_id": appointment_id})

@csrf_exempt
@login_required(login_url="login")
def payment_failure(request):
    return render(request, "payment/payment_failure.html")

@csrf_exempt
@login_required(login_url="login")
# View to display the invoice
def billing_invoice_view(request, payment_id):
    payment = get_object_or_404(Payment, payment_id=payment_id)
    patient = Patient.objects.get(user=request.user)
    template = 'view-invoice.html'
    context = {'patient':patient, 'payment': payment, }
    return render(request, template, context)


# Utility function to render HTML to PDF
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type="application/pdf")
    return None

# View to generate and download invoice PDF
@login_required(login_url="login")
@csrf_exempt
def download_invoice_pdf(request, payment_id):
    payment = get_object_or_404(Payment, payment_id=payment_id)
    
    context = {
        'payment': payment
    }
    
    pdf = render_to_pdf('billing_invoice.html', context)
    
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{payment_id}.pdf"'
        return response
    
    return HttpResponse("Error generating PDF", status=500)

# @csrf_exempt
# @login_required(login_url="login")
# # View to download the invoice as a PDF
# def download_invoice_view(request, payment_id):
#     payment = get_object_or_404(Payment, payment_id=payment_id)
#     template = get_template('billing_invoice.html')
#     html = template.render({'payment': payment})

#     # Generate PDF
#     pdf_options = {
#         'page-size': 'A4',
#         'encoding': 'UTF-8',
#         'no-outline': None,
#     }
#     pdf = pdfkit.from_string(html, False, options=pdf_options)

#     response = HttpResponse(pdf, content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="invoice_{payment_id}.pdf"'
#     return response