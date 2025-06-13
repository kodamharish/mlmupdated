from django.urls import path
from .views import *

urlpatterns = [
    
    path('transactions/', TransactionListCreateView.as_view() , name='transactions'),
    path('transactions/<int:transaction_id>/', TransactionDetailView.as_view(), name='transaction_details'),
    path('transactions/property/<int:property_id>/', TransactionByPropertyId.as_view(), name='transaction-by-property-id'),
    path('transactions/user-id/<int:user_id>/', TransactionByUserId.as_view(), name='transactions-by-user-id'),
    path('transactions/user-id/<int:user_id>/property-id/<int:property_id>/', TransactionByUserIdAndPropertyId.as_view(), name='transactions-by-user-id-property-id'),

    path('transactions/user-id/<int:user_id>/payment-type/<str:payment_type>/', TransactionByUserIdAndPaymentType.as_view(), name='transactions-by-user-id-payment-type'),
    path('transactions/payment-type/<str:payment_type>/', TransactionByPaymentType.as_view(), name='transactions-by-payment-type'),


    path('transactions/user-id/<int:user_id>/property-id/<int:property_id>/payment-type/<str:payment_type>/', TransactionByUserIdPropertyIdAndPaymentType.as_view(), name='transactions-by-user-id-property-id-payment-type'),
    path('transactions/property-id/<int:property_id>/payment-type/<str:payment_type>/', TransactionByPropertyIdAndPaymentType.as_view(), name='transactions-by-property-id-payment-type'),

    path('transactions/grouped/user-id/<int:user_id>/', TransactionsGroupedByPaymentTypeAPIView.as_view(), name='grouped-transactions'),

]