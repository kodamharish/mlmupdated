from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *
from decimal import Decimal
from property.models import  *
from transactions.models import *
from users.models import User



# ------------------ Commission Master Views ------------------

class CommissionMasterListCreateView(APIView):
    def get(self, request):
        try:
            commissions = CommissionMaster.objects.all()
            serializer = CommissionMasterSerializer(commissions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = CommissionMasterSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommissionMasterDetailView(APIView):
    def get(self, request, id):
        try:
            commission = get_object_or_404(CommissionMaster, id=id)
            serializer = CommissionMasterSerializer(commission)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            commission_master = get_object_or_404(CommissionMaster, id=id)
            serializer = CommissionMasterSerializer(commission_master, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            commission_master = get_object_or_404(CommissionMaster, id=id)
            commission_master.delete()
            return Response({"message": "Commission Master deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ------------------ Commission Views ------------------

class CommissionListCreateView(APIView):
    def get(self, request):
        try:
            commissions = Commission.objects.all()
            serializer = CommissionSerializer(commissions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = CommissionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommissionDetailView(APIView):
    def get(self, request, commission_id):
        try:
            commission = get_object_or_404(Commission, commission_id=commission_id)
            serializer = CommissionSerializer(commission)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, commission_id):
        try:
            commission = get_object_or_404(Commission, commission_id=commission_id)
            serializer = CommissionSerializer(commission, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, commission_id):
        try:
            commission = get_object_or_404(Commission, commission_id=commission_id)
            commission.delete()
            return Response({"message": "Commission deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommissionByReferralId(APIView):
    def get(self, request, referral_id):
        try:
            commissions = Commission.objects.filter(referral_id=referral_id)
            if not commissions.exists():
                return Response({"error": "No commissions found with this Referral ID"}, status=status.HTTP_404_NOT_FOUND)

            serializer = CommissionSerializer(commissions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# class CommissionByReferralId(APIView):
#     def get(self, request, referral_id):
#         try:
#             commissions = Commission.objects.filter(referral_id=referral_id).select_related('property_id')
#             serializer = CommissionSerializer(commissions, many=True)
#             return Response(serializer.data)
#         except Commission.DoesNotExist:
#             return Response({"error": "No commission records found for this referral ID."}, status=404)


class DistributeCommissionAPIView_old(APIView):
    def post(self, request, transaction_id):
        try:
            # Fetch the transaction
            transaction = Transaction.objects.get(pk=transaction_id)

            if transaction.payment_type != "Full-Amount":
                return Response({"error": "Commission is only distributed on Full-Amount payment."}, status=status.HTTP_400_BAD_REQUEST)

            property_instance = transaction.property_id

            # Get the user who made the transaction
            transacting_user = transaction.user_id

            # Start from the user who referred the transacting user
            current_referral_id = transacting_user.referred_by

            company_commission = transaction.company_commission
            current_level = 1
            total_distributed = Decimal(0)

            while current_referral_id and current_level <= 10:
                # Get user by referral_id
                try:
                    user = User.objects.get(referral_id=current_referral_id)
                except User.DoesNotExist:
                    break

                try:
                    master = CommissionMaster.objects.get(level_no=current_level)
                except CommissionMaster.DoesNotExist:
                    break

                # Calculate commission
                percentage = master.percentage
                commission_amount = (Decimal(percentage) / Decimal(100)) * company_commission
                total_distributed += commission_amount

                # Save commission log
                Commission.objects.create(
                    percentage=master,
                    transaction_id=str(transaction.transaction_id),
                    agent_id=str(user.user_id),
                    agent_name=user.first_name + " " + user.last_name if user.first_name else user.username,
                    amount=str(round(commission_amount, 2)),
                    referral_id=current_referral_id,
                    property_id=str(property_instance.property_id)
                )

                # Move to next referrer
                current_referral_id = user.referred_by
                current_level += 1

            # Calculate remaining commission
            undistributed_commission = company_commission - total_distributed

            # Save both distributed and remaining commissions in property
            property_instance.total_company_commission_distributed = round(total_distributed, 2)
            property_instance.remaining_company_commission = round(undistributed_commission, 2)
            property_instance.company_commission_status = "paid"
            property_instance.save()

            return Response({"message": "Commission distributed successfully."}, status=status.HTTP_200_OK)

        except Transaction.DoesNotExist:
            return Response({"error": "Transaction not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DistributeCommissionAPIView_new_old(APIView):
    def post(self, request, transaction_id):
        try:
            # Fetch the transaction
            transaction = Transaction.objects.get(pk=transaction_id)

            if transaction.payment_type != "Full-Amount":
                return Response(
                    {"error": "Commission is only distributed on Full-Amount payment."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            property_instance = transaction.property_id
            transacting_user = transaction.user_id
            company_commission = transaction.company_commission

            current_user = transacting_user  # Start with the user who made the transaction
            current_level = 1
            total_distributed = Decimal(0)

            while current_user and current_level <= 10:
                try:
                    master = CommissionMaster.objects.get(level_no=current_level)
                except CommissionMaster.DoesNotExist:
                    break

                # Calculate commission
                percentage = master.percentage
                commission_amount = (Decimal(percentage) / Decimal(100)) * company_commission
                total_distributed += commission_amount

                # Save commission log
                Commission.objects.create(
                    percentage=master,
                    transaction_id=str(transaction.transaction_id),
                    agent_id=str(current_user.user_id),
                    agent_name=current_user.first_name + " " + current_user.last_name if current_user.first_name else current_user.username,
                    amount=str(round(commission_amount, 2)),
                    referral_id=current_user.referral_id,
                    property_id=str(property_instance.property_id),
                    property_name=transaction.property_name,
                    username = transaction.username,
                    user_id = transaction.user_id
                )

                # Move to the next referrer in the chain
                if current_user.referred_by:
                    try:
                        current_user = User.objects.get(referral_id=current_user.referred_by)
                    except User.DoesNotExist:
                        break
                else:
                    break

                current_level += 1

            # Calculate remaining commission
            undistributed_commission = company_commission - total_distributed

            # Update property commission info
            property_instance.total_company_commission_distributed = round(total_distributed, 2)
            property_instance.remaining_company_commission = round(undistributed_commission, 2)
            property_instance.company_commission_status = "paid"
            property_instance.save()

            return Response({"message": "Commission distributed successfully."}, status=status.HTTP_200_OK)

        except Transaction.DoesNotExist:
            return Response({"error": "Transaction not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






class DistributeCommissionAPIView(APIView):
    def post(self, request, transaction_id):
        try:
            # Fetch the transaction
            transaction = Transaction.objects.get(pk=transaction_id)

            if transaction.payment_type != "Full-Amount":
                return Response(
                    {"error": "Commission is only distributed on Full-Amount payment."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            property_instance = transaction.property_id
            transacting_user = transaction.user_id
            company_commission = transaction.company_commission

            current_user = transacting_user  # Start with the user who made the transaction
            current_level = 1
            total_distributed = Decimal(0)

            while current_user and current_level <= 10:
                try:
                    master = CommissionMaster.objects.get(level_no=current_level)
                except CommissionMaster.DoesNotExist:
                    break

                # Calculate commission
                percentage = master.percentage
                commission_amount = (Decimal(percentage) / Decimal(100)) * company_commission
                total_distributed += commission_amount

                

                Commission.objects.create(
                percentage=master,
                transaction_id=transaction,  # Must be a Transaction instance
                agent_id=current_user,       # Must be a User instance
                agent_name=current_user.first_name + " " + current_user.last_name if current_user.first_name else current_user.username,
                amount=str(round(commission_amount, 2)),
                referral_id=current_user.referral_id,
                property_id=property_instance,  # ✅ Pass the Property instance here
                property_name=transaction.property_name,
                buyer_username=transaction.username,
                buyer_user_id=transaction.user_id
                )


                # Move to the next referrer in the chain
                if current_user.referred_by:
                    try:
                        current_user = User.objects.get(referral_id=current_user.referred_by)
                    except User.DoesNotExist:
                        break
                else:
                    break

                current_level += 1

            # Calculate remaining commission
            undistributed_commission = company_commission - total_distributed

            # Update property commission info
            property_instance.total_company_commission_distributed = round(total_distributed, 2)
            property_instance.remaining_company_commission = round(undistributed_commission, 2)
            property_instance.company_commission_status = "paid"
            property_instance.save()

            return Response({"message": "Commission distributed successfully."}, status=status.HTTP_200_OK)

        except Transaction.DoesNotExist:
            return Response({"error": "Transaction not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class CommissionPreviewAPIView(APIView):
    def get(self, request, transaction_id):
        commissions = Commission.objects.filter(transaction_id=transaction_id).order_by("percentage__level_no")

        if not commissions.exists():
            return Response({"message": "No commissions found for this transaction."}, status=status.HTTP_404_NOT_FOUND)

        data = []
        for commission in commissions:
            data.append({
                "level": commission.percentage.level_no,
                "agent_name": commission.agent_name,
                "referral_id": commission.referral_id,
                "amount": commission.amount,
                "percentage": str(commission.percentage.percentage) + " %",
            })

        return Response(data, status=status.HTTP_200_OK)





from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from property.models import Property
from users.models import User
from django.db.models import Sum

class AgentCommissionAPIView(APIView):
    def get(self, request, user_id):
        try:
            agent = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Agent not found"}, status=status.HTTP_404_NOT_FOUND)

        properties = Property.objects.filter(user_id=agent)

        commission_summary = properties.aggregate(
            total_agent_commission=Sum('agent_commission'),
            total_agent_commission_paid=Sum('agent_commission_paid'),
            total_agent_commission_balance=Sum('agent_commission_balance'),
        )

        properties_data = [
            {
                "property_id": prop.property_id,
                "property_title": prop.property_title,
                "agent_commission": prop.agent_commission,
                "agent_commission_paid": prop.agent_commission_paid,
                "agent_commission_balance": prop.agent_commission_balance
            }
            for prop in properties
        ]

        return Response({
            "agent_id": agent.user_id,
            "agent_name": f"{agent.first_name} {agent.last_name}",
            "commission_summary": commission_summary,
            "properties": properties_data
        }, status=status.HTTP_200_OK)







