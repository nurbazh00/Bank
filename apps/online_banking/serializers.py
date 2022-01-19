from rest_framework import serializers
from apps.online_banking.models import User, Account, Action, Transaction,\
    Transfer


class AuthSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=60)
    password = serializers.CharField(max_length=128)


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'middle_name',
                  'email', 'avatar', 'date_of_birth', 'country', 'city',
                  'password')


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'middle_name',
                  'avatar', 'date_of_birth', 'country', 'city',
                  'password')


class AccountSerializer(serializers.ModelSerializer):
    actions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Account
        fields = ('id', 'balance', 'actions')
        read_only_fields = ('id', 'balance', 'actions')


class ActionSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super(ActionSerializer, self).__init__(*args, **kwargs)
        if 'request' in self.context:
            self.fields['account'].queryset = self.fields['account']\
                .queryset.filter(user=self.context['view'].request.user)

    class Meta:
        model = Action
        fields = ('id', 'account', 'amount', 'date')
        read_only_fields = ('id', 'date')


class TransactionSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super(TransactionSerializer, self).__init__(*args, **kwargs)
        if 'request' in self.context:
            self.fields['account'].queryset = self.fields['account']\
                .queryset.filter(user=self.context['view'].request.user)

    class Meta:
        model = Transaction
        fields = ('id', 'account', 'date', 'merchant', 'amount')
        read_only_fields = ('id',)


class TransferSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super(TransferSerializer, self).__init__(*args, **kwargs)
        if 'request' in self.context:
            self.fields['from_account'].queryset = self.fields['from_account']\
                .queryset.filter(user=self.context['view'].request.user)

    to_account = serializers.CharField()

    def validate(self, data):
        try:
            data['to_account'] = Account.objects.get(pk=data['to_account'])
        except Exception as e:
            print(e)
            raise serializers.ValidationError(
                "No such account from serializer"
            )
        return data

    class Meta:
        model = Transfer
        fields = ('id', 'from_account', 'to_account', 'amount')
        read_only_fields = ('id',)
