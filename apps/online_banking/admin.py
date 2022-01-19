from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.online_banking.models import User, Account, Action, Transaction,\
    Transfer


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'first_name', 'last_name', 'middle_name', 'email', 'avatar',
        'date_of_birth', 'country', 'city'
    )

    def get_avatar(self, obj):
        if obj.avatar:
            return mark_safe(
                f'<img src={obj.avatar.url} width="100" />'
            )
        return '-'

    get_avatar.short_description = 'Фото'


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        'balance', 'user',
    )


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = (
        'amount', 'date', 'account'
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'amount', 'date', 'account', 'merchant'
    )


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = (
        'from_account', 'to_account', 'amount'
    )
