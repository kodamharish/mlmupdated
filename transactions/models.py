from django.db import models
from users.models import *
from property.models import *
from subscription.models import *

TRANSACTION_FOR_CHOICES = (
    ('property', 'Property'),
    ('subscription', 'Subscription'),
)

class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_transactions")
    property_id = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True, related_name='transactions')
    transaction_for = models.CharField(max_length=50, choices=TRANSACTION_FOR_CHOICES)  # NEW FIELD
    payment_type = models.CharField(max_length=100, blank=True, null=True)  # e.g., 'booking-amount', 'full-amount'
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_mode = models.CharField(max_length=100, blank=True, null=True)
    purchased_from = models.CharField(max_length=150, blank=True, null=True)
    purchased_type = models.CharField(max_length=150, blank=True, null=True)
    role = models.CharField(max_length=50, blank=True, null=True)
    username = models.CharField(max_length=150)
    remaining_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    receiver_upi_id = models.CharField(max_length=100, blank=True, null=True)
    plan_name = models.CharField(max_length=150, blank=True, null=True)
    subscription_variant = models.ForeignKey(SubscriptionPlanVariant, on_delete=models.CASCADE,blank=True, null=True)
    property_name = models.CharField(max_length=150, blank=True, null=True)
    property_value = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    company_commission = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    document_type = models.CharField(max_length=20, choices=[('invoice', 'Invoice'), ('receipt', 'Receipt')], blank=True, null=True)
    document_number = models.CharField(max_length=100, blank=True, null=True, unique=True)
    document_file = models.FileField(upload_to='transaction_documents/', blank=True, null=True)
    phone_pe_merchant_order_id = models.CharField(max_length=200, blank=True, null=True)
    phone_pe_order_id = models.CharField(max_length=200, blank=True, null=True)
    phone_pe_transaction_id = models.CharField(max_length=200, blank=True, null=True)
    transaction_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.username} ({self.transaction_for}, {self.payment_type})"


class UserProperty(models.Model):
    # STATUS_CHOICES = [
    #     ('booked', 'Booked'),
    #     ('purchased', 'Purchased'),
    # ]
    STATUS_CHOICES = [
        ('booked', 'Booked'),
        ('sold', 'Sold'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_properties')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='user_properties')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    booking_date = models.DateField(null=True, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'property')  # prevent duplicate booking/purchase by same user

    def __str__(self):
        return f"{self.user.username} - {self.property.property_title} ({self.status})"

