from rest_framework.routers import DefaultRouter
from django.urls import path, include
from apps.online_banking import views


app_name = 'v1'

router = DefaultRouter()

router.register('customer', views.CustomerDetail2)
router.register('account', views.AccountViewSet)
router.register('action', views.ActionViewSet)
router.register('transaction', views.TransactionViewSet)
router.register('transfer', views.TransferViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('customer/', views.CustomerDetail3.as_view(), name='customer'),
    path('transfer_alt/', views.CreateTransferView.as_view())
]
