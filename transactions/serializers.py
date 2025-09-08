from rest_framework import serializers
from .models import *
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
    plan_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    payment_type = serializers.ChoiceField(
        choices=['Full-Amount', 'Booking-Amount'],
        required=True
    )

    class Meta:
        model = Transaction
        fields = '__all__'

    def create(self, validated_data):
        request = self.context.get('request')
        doc_file = request.FILES.get('document_file') if request else None

        payment_type = validated_data['payment_type']  # Safe now

        doc_type = 'invoice' if payment_type == 'Full-Amount' else 'receipt'
        doc_number = generate_transaction_doc_number(doc_type)

        if doc_file:
            ext = os.path.splitext(doc_file.name)[1]
            doc_file.name = f"{doc_number}{ext}"
            validated_data['document_file'] = doc_file

        validated_data['document_type'] = doc_type
        validated_data['document_number'] = doc_number

        return Transaction.objects.create(**validated_data)


