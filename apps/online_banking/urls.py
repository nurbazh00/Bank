from rest_framework.routers import DefaultRouter
from django.urls import path, include

from apps.online_banking import views


app_name = 'v1'

router = DefaultRouter()

router.register('account', views.AccountViewSet)
router.register('action', views.ActionViewSet)
router.register('transaction', views.TransactionViewSet)
router.register('transfer', views.TransferViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth', views.UserAuthView.as_view(), name='auth'),
    path('users/', views.UserListCreateView.as_view(), name='users'),
    path('users/<int:pk>', views.UserDetailView.as_view()),
    path('transfer_alt/', views.CreateTransferView.as_view())
]
