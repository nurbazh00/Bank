from datetime import date

from django.conf import settings
from django.db import models


class Customer(models.Model):
    first_name = models.CharField(verbose_name='Имя',
                                  max_length=255)
    last_name = models.CharField(verbose_name='Фамилия',
                                 max_length=255,
                                 null=True, blank=True)
    middle_name = models.CharField(verbose_name='Отчество',
                                   max_length=255,
                                   null=True, blank=True)
    image = models.ImageField(verbose_name='Фото',
                               upload_to='Customer',
                               null=True, blank=True)
    date_of_birth = models.DateField(verbose_name='Дата рождения',
                                     default=date.today)
    country = models.CharField(verbose_name='Страна',
                               max_length=255,
                               null=True, blank=True)
    city = models.CharField(verbose_name='Город',
                            max_length=255,
                            null=True, blank=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.first_name}, {self.last_name}'


class Account(models.Model):
    balance = models.DecimalField(default=0, max_digits=9, decimal_places=2)

    class Meta:
        verbose_name = 'Счет'
        verbose_name_plural = 'Счета'

    def __str__(self):
        return f'{self.id} of {self.user.username}'


class Action(models.Model):
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE,
                                related_name='actions')

    class Meta:
        verbose_name = 'Пополнение счета'
        verbose_name_plural = 'Пополнение счетов'

    def __str__(self):
        return f'Account number {self.account.id}' +\
            f'was changed on {str(self.amount)}'


class Transaction(models.Model):
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    merchant = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'

    def __str__(self):
        return f'Account number {self.account.id}' +\
            f'sent {str(self.amount)} to {self.merchant}'


class Transfer(models.Model):
    from_account = models.ForeignKey(Account, on_delete=models.CASCADE,
                                     related_name='from_account')
    to_account = models.ForeignKey(Account, on_delete=models.CASCADE,
                                   related_name='to_account')
    amount = models.DecimalField(max_digits=9, decimal_places=2)

    class Meta:
        verbose_name = 'Перевод'
        verbose_name_plural = 'Переводы'

    def __str__(self):
        return f'От кого: {self.from_account}, Сумма: {self.amount}'
