from django.contrib.auth.hashers import make_password
from rest_framework import status, generics, viewsets, mixins
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.online_banking.mixins import ServiceExceptionHandlerMixin
from apps.online_banking.models import User, Action, Account, Transaction, \
    Transfer
from apps.online_banking.serializers import AuthSerializer, \
    UserCreateSerializer, UserDetailSerializer, ActionSerializer,\
    AccountSerializer, TransactionSerializer, TransferSerializer
from apps.online_banking.services import check_balance_to_withdraw, \
    filter_user_account, check_account_exists, make_transaction, make_transfer


class UserAuthView(APIView):
    permission_classes = [AllowAny]
    serializer_class = AuthSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(email=serializer.data.get('email')).first()

        if user is None:
            return Response(
                data={'error': 'Пользователь не найден'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not user.check_password(serializer.data.get('password')):
            return Response(
                data={'error': 'Не верный пароль'},
                status=status.HTTP_404_NOT_FOUND,
            )

        user_token, created = Token.objects.get_or_create(user=user)
        return Response(data={'token': user_token.key},
                        status=status.HTTP_200_OK)


class UserListCreateView(generics.ListCreateAPIView):
    permission_classes = (AllowAny,)
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserCreateSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.password = make_password(instance.password)
        instance.save()


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserDetailSerializer

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class AccountViewSet(viewsets.GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin):
    serializer_class = AccountSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Account.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(datetime=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            filter_user_account(**serializer.validated_data)
        except ValueError:
            content = {'error': "Account doesn't exist"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            check_account_exists(**serializer.validated_data)
        except ValueError:
            content = {'error': 'No such account'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class ActionViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin,
                    mixins.CreateModelMixin):
    serializer_class = ActionSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Action.objects.all()

    def get_queryset(self):
        accounts = Account.objects.filter(user=self.request.user)
        return self.queryset.filter(account__in=accounts)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            account = Account.objects.filter(
                user=self.request.user).get(pk=self.request.data['account'])
        except Exception as e:
            print(e)
            content = {'error': 'No such account'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(account=account)

        try:
            check_balance_to_withdraw(**serializer.validated_data)
        except ValueError:
            content = {'error': 'Not enough money'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class TransactionViewSet(viewsets.GenericViewSet,
                         mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin):
    serializer_class = TransactionSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Transaction.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            account = Account.objects.filter(
                user=self.request.user).get(pk=self.request.data['account'])
        except Exception as e:
            print(e)
            content = {'error': 'No such account'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(account=account)

        try:
            make_transaction(**serializer.validated_data)
        except ValueError:
            content = {'error': 'Not enough money'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def get_queryset(self):
        accounts = Account.objects.filter(user=self.request.user)
        return  self.queryset.filter(account__in=accounts)


class TransferViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      ServiceExceptionHandlerMixin):

    serializer_class = TransferSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Transaction.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            make_transfer(**serializer.validated_data)
        except ValueError:
            content = {'error': 'Not enough money'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def get_queryset(self):
        accounts = Account.objects.filter(user=self.request.user)
        return self.queryset.filter(from_account__in=accounts)


class CreateTransferView(ServiceExceptionHandlerMixin, APIView):
    serializer_class = TransferSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Transfer.objects.all()

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        from_account = filter_user_account(
            self.request.user,
            self.request.data['from_account']
        )

        to_account = check_account_exists(self.request.data['to_account'])

        make_transfer(
            from_account,
            to_account,
            float(self.request.data['amount'])
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
