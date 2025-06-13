from django.urls import path
from .views import *

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),

    path('roles/', RoleListCreateView.as_view(), name='role-list-create'),
    path('roles/<int:role_id>/', RoleDetailView.as_view(), name='role-detail'),

    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),

    path('users/role/<str:role_name>/', UsersByRoleAPIView.as_view(), name='users-by-role'), 
    path('users/status/<str:user_status>/', UsersByStatus.as_view(), name='users-by-status'), 

    path('agents/referral-id/<str:referral_id>/', AgentsByReferralIdAPIView.as_view(), name='agents-by-referral-id'), 
    path('counts/', CountAPIView.as_view(), name='counts'),

    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('verify-otp-reset-password/', VerifyOTPAndResetPasswordView.as_view(), name='verify-reset'),

    path('meeting-requests/', MeetingRequestListCreateView.as_view(), name='meeting-requests'),
    path('meeting-requests/<int:request_id>/', MeetingRequestDetailView.as_view(), name='meeting-request-detail'),
    path('scheduled-meetings/', ScheduledMeetingListCreateView.as_view(), name='scheduled-meetings'),
    path('scheduled-meetings/<int:scheduled_meeting_id>/', ScheduledMeetingDetailView.as_view(), name='scheduled-meeting-detail'),


    path('meeting-requests/user-id/<int:user_id>/', MeetingRequestsByUserIdAPIView.as_view(), name='meeting-requests-user-id'),





    


]