
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from property.models import  *
import random
from django.core.mail import send_mail
from django.utils.cache import caches
from mlm.settings import *

# Use Django's cache framework to store OTP temporarily
cache = caches['default']







class LoginAPIView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            user = User.objects.get(email=email)
            print(user)
            if check_password(password, user.password):
                # Fetch the user's roles
                roles = user.roles.values_list('role_name', flat=True)  # Get role names as a list
                
                return Response(
                    {
                        "message": "Login successful",
                        "user_id": user.user_id,
                        "referral_id":user.referral_id,
                        "referred_by": user.referred_by,
                        "first_name":user.first_name,
                        "last_name": user.last_name,
                        "email": user.email,
                        "phone_number": user.phone_number,
                        "roles": list(roles),  # Convert QuerySet to list
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)




# Logout API 
class LogoutAPIView(APIView):
    def post(self, request):
        return Response({"message": "Logged out successfully!"}, status=status.HTTP_200_OK)
    


class RoleListCreateView(APIView):
    def get(self, request):
        try:
            roles = Role.objects.all()
            serializer = RoleSerializer(roles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = RoleSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RoleDetailView(APIView):
    def get(self, request, role_id):
        try:
            role = get_object_or_404(Role, role_id=role_id)
            serializer = RoleSerializer(role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, role_id):
        try:
            role = get_object_or_404(Role, role_id=role_id)
            serializer = RoleSerializer(role, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, role_id):
        try:
            role = get_object_or_404(Role, role_id=role_id)
            role.delete()
            return Response({"message": "Role deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class UserListCreateView(APIView):
    def get(self, request):
        try:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data = request.data.copy()

            if "password" in data and not data["password"].startswith("pbkdf2_sha256$"):
                data["password"] = make_password(data["password"])

            role_ids = data.get("role_ids", [])
            agent_role = Role.objects.filter(role_name="Agent").first()

            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                user = serializer.save()


                if agent_role and agent_role in user.roles.all():
                    agent_count = User.objects.filter(roles=agent_role).exclude(referral_id__isnull=True).exclude(user_id=user.user_id).count()
                    referral_id = f"SRP{str(agent_count + 1).zfill(6)}"
                    user.referral_id = referral_id
                    user.save(update_fields=['referral_id'])


                return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class UserDetailView(APIView):
    def get(self, request, user_id):
        try:
            user = get_object_or_404(User, user_id=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, user_id):
        try:
            user = get_object_or_404(User, user_id=user_id)
            data = request.data.copy()
            if 'password' in data:
                data['password'] = make_password(data['password'])  # Hash new password need to remove
            serializer = UserSerializer(user, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, user_id):
        try:
            user = get_object_or_404(User, user_id=user_id)
            user.delete()
            return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class UsersByRoleAPIView(APIView):
    def get(self, request, role_name):
        try:
            role = Role.objects.get(role_name=role_name)
            users = User.objects.filter(roles=role).distinct()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=200)
        except Role.DoesNotExist:
            return Response({"error": f"Role '{role_name}' not found"}, status=404)



class UsersByStatus(APIView):
    def get(self, request, user_status):
        try:
            properties = User.objects.filter(status=user_status)
            serializer = UserSerializer(properties, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# class AgentsByReferralIdAPIView(APIView):
#     def get(self, request, referral_id):
#         try:
#             users = User.objects.filter(referred_by=referral_id).order_by('created_at')
#             active = users.filter(status__iexact='Active') 
#             inactive = users.filter(status__iexact='Inactive')
#             count = users.count()  # Total users
#             active_count = users.filter(status__iexact='Active').count()  
#             inactive_count = users.filter(status__iexact='Inactive').count()  

#             serializer = UserSerializer(users, many=True)
#             return Response({
#                 "users": serializer.data,
#                 "active_agents": serializer.data,
#                 "users": serializer.data,
#                 "total_agents": count,
#                 "total_active_agents": active_count,
#                 "total_inactive_agents": inactive_count
#             }, status=200)
#         except User.DoesNotExist:
#             return Response({"error": f"Users with '{referral_id}' not found"}, status=404)



class AgentsByReferralIdAPIView(APIView):
    def get(self, request, referral_id):
        try:
            users = User.objects.filter(referred_by=referral_id).order_by('created_at')
            active_users = users.filter(status__iexact='Active')
            inactive_users = users.filter(status__iexact='Inactive')

            users_serializer = UserSerializer(users, many=True)
            active_serializer = UserSerializer(active_users, many=True)
            inactive_serializer = UserSerializer(inactive_users, many=True)

            return Response({
                "agents": users_serializer.data,
                "active_agents": active_serializer.data,
                "inactive_agents": inactive_serializer.data,
                "total_agents": users.count(),
                "total_active_agents": active_users.count(),
                "total_inactive_agents": inactive_users.count()
            }, status=200)
        except User.DoesNotExist:
            return Response({"error": f"Users with referral ID '{referral_id}' not found"}, status=404)



# class CountAPIView(APIView):
#     def get(self, request):
#         # Calculate the date one month ago from today
#         one_month_ago = timezone.now() - timedelta(days=30)

#         # Aggregate counts for users
#         user_counts = User.objects.aggregate(
#             # Role based counts
#             total_admins=Count('user_id', filter=Q(roles__role_name__iexact='Admin'), distinct=True),
#             total_clients=Count('user_id', filter=Q(roles__role_name__iexact='Client'), distinct=True),
#             total_agents=Count('user_id', filter=Q(roles__role_name__iexact='Agent'), distinct=True),
            
#             # Active/Inactive counts (charfield comparison)
#             total_active_users=Count('user_id', filter=Q(status__iexact="Active"), distinct=True),
#             total_inactive_users=Count('user_id', filter=Q(status__iexact="Inactive"), distinct=True),
#         )

#         # Aggregate counts for properties
#         property_counts = Property.objects.aggregate(
#             total_properties=Count('property_id', distinct=True),
#             total_latest_properties=Count('property_id', distinct=True, filter=Q(created_at__gte=one_month_ago)),
#         )

#         # Combine the counts
#         counts = {**user_counts, **property_counts}

#         return Response(counts, status=status.HTTP_200_OK)



class CountAPIView(APIView):
    def get(self, request):
        # Calculate the date one month ago from today
        one_month_ago = timezone.now() - timedelta(days=30)

        # Aggregate counts for users
        user_counts = User.objects.aggregate(
            total_admins=Count('user_id', filter=Q(roles__role_name__iexact='Admin'), distinct=True),
            total_clients=Count('user_id', filter=Q(roles__role_name__iexact='Client'), distinct=True),
            total_agents=Count('user_id', filter=Q(roles__role_name__iexact='Agent'), distinct=True),
            total_active_users=Count('user_id', filter=Q(status__iexact="Active"), distinct=True),
            total_inactive_users=Count('user_id', filter=Q(status__iexact="Inactive"), distinct=True),
        )

        # Aggregate counts for properties
        property_counts = Property.objects.aggregate(
            total_properties=Count('property_id', distinct=True),
            total_latest_properties=Count('property_id', filter=Q(created_at__gte=one_month_ago), distinct=True),

            # Status-based counts
            total_sold_properties=Count('property_id', filter=Q(status__iexact='Sold'), distinct=True),
            total_booked_properties=Count('property_id', filter=Q(status__iexact='Booked'), distinct=True),
            total_available_properties=Count('property_id', filter=Q(status__iexact='Available'), distinct=True),

            # Approval status-based counts
            total_pending_properties=Count('property_id', filter=Q(approval_status__iexact='Pending'), distinct=True),
            total_approved_properties=Count('property_id', filter=Q(approval_status__iexact='Approved'), distinct=True),
            total_rejected_properties=Count('property_id', filter=Q(approval_status__iexact='Rejected'), distinct=True),
        )

        # Combine the counts
        counts = {**user_counts, **property_counts}

        return Response(counts, status=status.HTTP_200_OK)


class SendOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        otp = random.randint(1000, 9999)  # Generate a 4-digit OTP
        cache.set(f'otp_{email}', otp, timeout=300)  # Store OTP for 5 minutes
        
        # Send OTP via email
        send_mail(
            subject='Password Reset OTP',
            message=f'Your OTP for password reset is {otp}. It is valid for 5 minutes.',
            from_email=EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
        
        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)





class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({'error': 'Email and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)

        stored_otp = cache.get(f'otp_{email}')
        if stored_otp and str(stored_otp) == str(otp):
            cache.delete(f'otp_{email}')
            cache.set(f'otp_verified_{email}', True, timeout=300)  # OTP verified flag valid for 5 minutes
            return Response({'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)





class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')

        if not email or not new_password:
            return Response({'error': 'Email and new password are required'}, status=status.HTTP_400_BAD_REQUEST)

        otp_verified = cache.get(f'otp_verified_{email}')
        if not otp_verified:
            return Response({'error': 'OTP not verified or session expired'}, status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(email=email)
            user.password = make_password(new_password)
            user.save()
            cache.delete(f'otp_verified_{email}')  # Clean up the flag
            return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)








class VerifyOTPAndResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        if not email or not otp:
            return Response({'error': 'Email and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)

        stored_otp = cache.get(f'otp_{email}')
        if stored_otp and str(stored_otp) == str(otp):
            cache.delete(f'otp_{email}')

            # Case 1: Only verify OTP
            if not new_password:
                cache.set(f'otp_verified_{email}', True, timeout=300)
                return Response({'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)

            # Case 2: OTP + new password provided → reset password
            try:
                user = User.objects.get(email=email)
                user.password = make_password(new_password)
                user.save()
                return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)




# Meetings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

class MeetingRequestListCreateView(APIView):
    def get(self, request):
        try:
            requests = MeetingRequest.objects.all().order_by('-created_at')
            serializer = MeetingRequestSerializer(requests, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = MeetingRequestSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Meeting request created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MeetingRequestDetailView(APIView):
    def get(self, request, request_id):
        try:
            req = get_object_or_404(MeetingRequest, request_id=request_id)
            serializer = MeetingRequestSerializer(req)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, request_id):
        try:
            req = get_object_or_404(MeetingRequest, request_id=request_id)
            serializer = MeetingRequestSerializer(req, data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, request_id):
        try:
            req = get_object_or_404(MeetingRequest, request_id=request_id)
            req.delete()
            return Response({"message": "Meeting request deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class ScheduledMeetingListCreateView(APIView):
#     def get(self, request):
#         try:
#             meetings = ScheduledMeeting.objects.all().order_by('-scheduled_date')
#             serializer = ScheduledMeetingSerializer(meetings, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def post(self, request):
#         try:
#             serializer = ScheduledMeetingSerializer(data=request.data)
#             if serializer.is_valid():
#                 meeting_request = serializer.validated_data['request']
#                 meeting_request.is_scheduled = True
#                 meeting_request.save()
#                 serializer.save()
#                 return Response({"message": "Meeting scheduled successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class ScheduledMeetingListCreateView(APIView):
    def get(self, request):
        try:
            meetings = ScheduledMeeting.objects.all().order_by('-scheduled_date')
            serializer = ScheduledMeetingSerializer(meetings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = ScheduledMeetingSerializer(data=request.data)
            if serializer.is_valid():
                meeting_request = serializer.validated_data['request']
                meeting_request.is_scheduled = True
                meeting_request.save()

                # Save the ScheduledMeeting instance
                scheduled_meeting = serializer.save()

                # Extract data from the saved ScheduledMeeting instance
                name = scheduled_meeting.request.name
                referral_id = scheduled_meeting.request.referral_id
                profile_type = scheduled_meeting.request.profile_type
                meeting_link = scheduled_meeting.meeting_link
                scheduled_date = scheduled_meeting.scheduled_date
                scheduled_time = scheduled_meeting.scheduled_time
                recipient_email = scheduled_meeting.request.email  # email from related Request model

                # Email content
                subject = "Meeting Scheduled Successfully"
                message = (
                    f"Dear {name},\n\n"
                    f"Your meeting has been scheduled successfully.\n\n"
                    f"Details:\n"
                    f"Name: {name}\n"
                    f"Referral ID: {referral_id}\n"
                    f"Profile Type: {profile_type}\n"
                    f"Meeting Link: {meeting_link}\n"
                    f"Scheduled Date: {scheduled_date}\n"
                    f"Scheduled Time: {scheduled_time}\n\n"
                    f"Thank you!"
                )

                # Send the email
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [recipient_email],
                    fail_silently=False,
                )

                return Response({"message": "Meeting scheduled successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# views.py

class ScheduledMeetingDetailView(APIView):
    def get(self, request, scheduled_meeting_id):
        try:
            meeting = get_object_or_404(ScheduledMeeting, scheduled_meeting_id=scheduled_meeting_id)
            serializer = ScheduledMeetingSerializer(meeting)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def put(self, request, scheduled_meeting_id):
    #     try:
    #         meeting = get_object_or_404(ScheduledMeeting, scheduled_meeting_id=scheduled_meeting_id)
    #         serializer = ScheduledMeetingSerializer(meeting, data=request.data,partial=True)
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response(serializer.data, status=status.HTTP_200_OK)
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     except Exception as e:
    #         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def put(self, request, scheduled_meeting_id):
        try:
            meeting = get_object_or_404(ScheduledMeeting, scheduled_meeting_id=scheduled_meeting_id)
            old_status = meeting.status  # Save the current status

            serializer = ScheduledMeetingSerializer(meeting, data=request.data, partial=True)
            if serializer.is_valid():
                updated_meeting = serializer.save()

                # Check if status has changed to 'cancelled' or 'completed'
                new_status = updated_meeting.status
                if old_status != new_status and new_status in ['cancelled', 'completed']:
                    name = updated_meeting.request.name
                    recipient_email = updated_meeting.request.email
                    scheduled_date = updated_meeting.scheduled_date
                    scheduled_time = updated_meeting.scheduled_time
                    meeting_link = updated_meeting.meeting_link

                    subject = f"Meeting {new_status.capitalize()}"
                    message = (
                        f"Dear {name},\n\n"
                        f"Your scheduled meeting has been {new_status}.\n\n"
                        f"Meeting Details:\n"
                        f"Date: {scheduled_date}\n"
                        f"Time: {scheduled_time}\n"
                        f"Link: {meeting_link if meeting_link else 'N/A'}\n\n"
                        f"Thank you."
                    )

                    send_mail(
                        subject,
                        message,
                        settings.EMAIL_HOST_USER,
                        [recipient_email],
                        fail_silently=False,
                    )

                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, scheduled_meeting_id):
        try:
            meeting = get_object_or_404(ScheduledMeeting, scheduled_meeting_id=scheduled_meeting_id)
            # Unmark the original request as scheduled (optional logic)
            if meeting.request:
                meeting.request.is_scheduled = False
                meeting.request.save()
            meeting.delete()
            return Response({"message": "Scheduled meeting deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class MeetingRequestsByUserIdAPIView(APIView):
    def get(self, request,user_id):
        requests = MeetingRequest.objects.all().filter(user_id=user_id)
        serializer = MeetingRequestSerializer(requests, many=True)
        return Response(serializer.data)
    

