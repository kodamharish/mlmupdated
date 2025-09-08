from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from subscription.models import SubscriptionPlanVariant
from users.models import User
from .utils import *  
from subscription.models import *
from transactions.models import *
from users.models import *
import os
from datetime import date
from django.utils import timezone
from io import BytesIO
from datetime import datetime
from django.core.files.base import ContentFile
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import os
from django.conf import settings





class SubscriptionInitiatePaymentAPIView(APIView):
    def post(self, request):
        try:
            user_id = request.data.get("user_id")
            variant_id = request.data.get("variant_id")
            redirect_url = request.data.get("redirect_url")

            if not all([user_id, variant_id, redirect_url]):
                return Response({"error": "Missing required fields"}, status=400)

            user = User.objects.get(user_id=user_id)
            variant = SubscriptionPlanVariant.objects.get(variant_id=variant_id)
            amount = int(variant.price * 100)  # PhonePe requires amount in paise

            result = initiate_payment(amount=amount, redirect_url=redirect_url)

            return Response({
                "merchant_order_id": result["merchant_order_id"],
                "payment_url": result["redirect_url"]
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        except SubscriptionPlanVariant.DoesNotExist:
            return Response({"error": "Subscription plan not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)




class SubscriptionConfirmPaymentAPIView(APIView):
    def post(self, request):
        try:
            merchant_order_id = request.data.get("merchant_order_id")
            user_id = request.data.get("user_id")
            variant_id = request.data.get("variant_id")
            

            if not all([merchant_order_id, user_id, variant_id]):
                return Response({"error": "Missing required fields"}, status=400)

            # Step 1: Check payment status from PhonePe
            payment_status_data = check_payment_status(merchant_order_id)
            payment_state = payment_status_data.get("status")

            if payment_state != "COMPLETED":
                return Response({
                    **payment_status_data,
                    "message": "Payment not completed"
                }, status=202)

            # Step 2: Get user and variant
            user = User.objects.get(user_id=user_id)
            variant = SubscriptionPlanVariant.objects.get(variant_id=variant_id)
            plan_name = variant.plan_id.plan_name
            price = variant.price
            user.status = 'active'
            user.save()

            # Step 3: Extract payment details
            payment_details = payment_status_data.get("payment_details", [])
            phone_pe_transaction_id = payment_details[0]["transaction_id"] if payment_details else None
            payment_mode_from_response = payment_details[0]["payment_mode"] if payment_details else None


            # Step 5: Create subscription
            Subscription.objects.create(
                user_id=user,
                subscription_variant=variant,
                subscription_status='paid'
            )

            # Step 6: Create transaction
            Transaction.objects.create(
                user_id=user,
                transaction_for='subscription',
                paid_amount=price,
                payment_mode=payment_mode_from_response,
                #purchased_from='Online',
                subscription_variant = variant,
                plan_name=plan_name,
                username=user.username,
                phone_pe_merchant_order_id=payment_status_data.get("merchant_order_id"),
                phone_pe_order_id=payment_status_data.get("order_id"),
                phone_pe_transaction_id=phone_pe_transaction_id
            )

            return Response({
                "message": "Payment verified and subscription created successfully",
                **payment_status_data
            }, status=201)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        except SubscriptionPlanVariant.DoesNotExist:
            return Response({"error": "Subscription plan not found"}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)




class PropertyInitiatePaymentAPIView(APIView):
    def post(self, request):
        try:
            user_id = request.data.get("user_id")
            property_id = request.data.get("property_id")
            payment_type = request.data.get("payment_type")
            redirect_url = request.data.get("redirect_url")

            if not all([user_id, property_id, payment_type, redirect_url]):
                return Response({"error": "Missing required fields"}, status=400)

            user = User.objects.get(user_id=user_id)
            property_obj = Property.objects.get(property_id=property_id)

            if payment_type == "Booking-Amount":
                amount = int(property_obj.booking_amount * 100)
            elif payment_type == "Full-Amount":
                amount = int(property_obj.property_value_without_booking_amount * 100)
            else:
                return Response({"error": "Invalid payment_type. Use 'Booking-Amount' or 'Full-Amount'"}, status=400)

            result = initiate_payment(amount=amount, redirect_url=redirect_url)

            return Response({
                "merchant_order_id": result["merchant_order_id"],
                "payment_url": result["redirect_url"]
            }, status=200)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        except Property.DoesNotExist:
            return Response({"error": "Property not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)




# Document number generation function (reuse)

def generate_transaction_doc_number(doc_type):
    prefix = 'INV' if doc_type == 'invoice' else 'REC'
    
    count = Transaction.objects.filter(
        document_type=doc_type
    ).count() + 1

    return f"{prefix}{count:04d}"


class PropertyConfirmPaymentAPIView(APIView):
    def post(self, request):
        try:
            user_id = request.data.get("user_id")
            property_id = request.data.get("property_id")
            payment_type = request.data.get("payment_type")  # 'Full-Amount' or 'Booking-Amount'
            merchant_order_id = request.data.get("merchant_order_id")
            doc_file = request.FILES.get("document_file")

            if not all([user_id, property_id, payment_type, merchant_order_id]):
                return Response({"error": "Missing required fields"}, status=400)

            user = User.objects.get(user_id=user_id)
            property_obj = Property.objects.get(property_id=property_id)

            # Step 1: Check payment status
            payment_status_data = check_payment_status(merchant_order_id)
            payment_state = payment_status_data.get("status")

            if payment_state != "COMPLETED":
                return Response({
                    **payment_status_data,
                    "message": "Payment not completed"
                }, status=202)

            # Step 2: Extract payment details
            payment_details = payment_status_data.get("payment_details", [])
            phone_pe_transaction_id = payment_details[0]["transaction_id"] if payment_details else None
            payment_mode = payment_details[0]["payment_mode"] if payment_details else None

            # Step 3: Determine amounts and logic
            if payment_type == "Booking-Amount":
                new_status = "booked"
                paid_amount = property_obj.booking_amount
                remaining_amount = property_obj.property_value_without_booking_amount

                date_field = "booking_date"
                doc_type = "receipt"
            elif payment_type == "Full-Amount":
                new_status = "purchased"
                paid_amount = property_obj.property_value_without_booking_amount
                remaining_amount = 0.00
                date_field = "purchase_date"
                doc_type = "invoice"
            else:
                return Response({"error": "Invalid payment_type"}, status=400)

            # Step 4: Generate document number and optionally rename file
            doc_number = generate_transaction_doc_number(doc_type)

            if doc_file:
                ext = os.path.splitext(doc_file.name)[1]
                doc_file.name = f"{doc_number}{ext}"

            # Step 5: Check for duplicate transactions
            if UserProperty.objects.filter(user=user, property=property_obj, status=new_status).exists():
                return Response({"error": f"Property already {new_status} by this user"}, status=400)

            if property_obj.status == "purchased":
                return Response({"error": "Property already purchased"}, status=400)
            
            # Extract user roles
            user_roles = user.roles.all().values_list("role_name", flat=True)
            role_str = user_roles[0] if user_roles else None


            # Step 6: Create Transaction
            transaction = Transaction.objects.create(
                user_id=user,
                username = user.username,
                property_id=property_obj,
                property_name = property_obj.property_title,
                property_value = property_obj.total_property_value,
                remaining_amount = remaining_amount,
                company_commission = property_obj.company_commission,
                transaction_for="property",
                role=role_str,
                paid_amount=paid_amount,
                payment_mode=payment_mode,
                phone_pe_merchant_order_id=payment_status_data.get("merchant_order_id"),
                phone_pe_order_id=payment_status_data.get("order_id"),
                phone_pe_transaction_id=phone_pe_transaction_id,
                payment_type=payment_type,
                document_type=doc_type,
                document_number=doc_number,
                document_file=doc_file,
            )

            generate_invoice_pdf(transaction, user, property_obj, doc_number,doc_type)

            # Step 7: Create or update UserProperty
            user_property, created = UserProperty.objects.get_or_create(
                user=user,
                property=property_obj,
                defaults={"status": new_status, date_field: timezone.now().date()}
            )

            if not created and new_status == "purchased" and user_property.status != "purchased":
                user_property.status = "purchased"
                setattr(user_property, date_field, timezone.now().date())
                user_property.save()

            # Step 8: Update Property status
            if new_status == "purchased" and property_obj.status == "booked":
                property_obj.status = "purchased"
            elif new_status == "booked" and property_obj.status == "available":
                property_obj.status = "booked"
            property_obj.save()

            return Response({
                "message": "Payment verified and transaction recorded successfully",
                **payment_status_data
            }, status=201)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        except Property.DoesNotExist:
            return Response({"error": "Property not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)




