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

    path('leads/', LeadListCreateView.as_view(), name='lead-list-create'),
    path('leads/<int:id>/', LeadDetailView.as_view(), name='lead-detail'),

    path('carousel/', CarouselItemListCreateView.as_view(), name='carousel-list-create'),
    path('carousel/<int:pk>/', CarouselItemDetailView.as_view(), name='carousel-detail'),


    path('training-materials/', TrainingMaterialListCreateView.as_view(), name='training_material_list_create'),
    path('training-materials/<int:id>/', TrainingMaterialDetailView.as_view(), name='training_material_detail'),


    path('phonenumbers/', PhonenumberListCreateView.as_view(), name='phonenumber-list-create'),
    path('phonenumbers/<int:id>/', PhonenumberDetailView.as_view(), name='phonenumber-detail'),


    path('business/', BusinessListCreateView.as_view(), name='business-list-create'),
    path('business/<int:business_id>/', BusinessDetailView.as_view(), name='business-detail'),



]