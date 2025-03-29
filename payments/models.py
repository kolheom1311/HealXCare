from django.db import models
from doctor.models import Appointment  # Ensure this is the correct import

# Create your models here.
class Payment(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="payments")  # Allow multiple payments per appointment
    payment_id = models.CharField(max_length=100, blank=True, null=True, unique=False)  # Remove unique=True
    order_id = models.CharField(max_length=100, unique=True)  # Keep unique to avoid duplicates in Razorpay
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Payment {self.order_id} - {self.status}"
    

    
# class Payment(models.Model):
#     appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="payment")
#     payment_id = models.CharField(max_length=100, unique=True)
#     order_id = models.CharField(max_length=100, unique=True)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     status = models.CharField(max_length=20, choices=[
#         ('pending', 'Pending'),
#         ('paid', 'Paid'),
#         ('failed', 'Failed'),
#     ], default='pending')
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Payment {self.payment_id} - {self.status}"


