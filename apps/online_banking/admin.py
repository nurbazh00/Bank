from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.online_banking.models import Customer, Account, Action, Transaction,\
    Transfer


@admin.register(Customer)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'first_name', 'last_name', 'middle_name',
        'date_of_birth', 'country', 'city', 'image'
    )

    def get_avatar(self, obj):
        if obj.avatar:
            return mark_safe(
                f'<img src={obj.avatar.url} width="100" />'
            )
        return '-'

    get_avatar.short_description = 'Фото'


admin.site.register(Account)
admin.site.register(Action)
admin.site.register(Transaction)
admin.site.register(Transfer)
