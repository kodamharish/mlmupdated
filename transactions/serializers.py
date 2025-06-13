from rest_framework import serializers
from .models import *


# class TransactionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Transaction
#         fields = '__all__'





import os
from datetime import datetime
from rest_framework import serializers
from .models import Transaction

# Helper function to generate document number
def generate_transaction_doc_number(doc_type):
    from datetime import date
    today = date.today()
    prefix = 'INV' if doc_type == 'invoice' else 'REC'
    date_str = today.strftime("%Y%m%d")

    # Count transactions for today and this document type
    count = Transaction.objects.filter(
        document_type=doc_type,
        transaction_date__date=today
    ).count() + 1

    return f"{prefix}-{date_str}-{count:05d}"

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

    def validate_payment_type(self, value):
        allowed = ['Full-Amount', 'Booking-Amount']
        if value not in allowed:
            raise serializers.ValidationError("Invalid payment_type. Allowed values: Full-Amount, Booking-Amount.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        doc_file = request.FILES.get('document_file') if request else None

        payment_type = validated_data.get('payment_type')
        if not payment_type:
            raise serializers.ValidationError({"payment_type": "This field is required."})

        doc_type = 'invoice' if payment_type == 'Full-Amount' else 'receipt'
        doc_number = generate_transaction_doc_number(doc_type)

        # Rename uploaded file if it exists
        if doc_file:
            ext = os.path.splitext(doc_file.name)[1]
            doc_file.name = f"{doc_number}{ext}"
            validated_data['document_file'] = doc_file  # ✅ override here

        # Add document fields
        validated_data['document_type'] = doc_type
        validated_data['document_number'] = doc_number

        return Transaction.objects.create(**validated_data)



