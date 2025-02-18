from django.db import models
from doctor.models import Appointment  # Ensure this is the correct import

# Create your models here.
class Payment(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100, unique=True)
    order_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.payment_id} - {self.status}"
