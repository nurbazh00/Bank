from datetime import date

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token


class UserManager(BaseUserManager):
    """ This is a manager for Account class """
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('User must have an Email address')

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email=self.normalize_email(email),
                                password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(verbose_name='Имя',
                                  max_length=255)
    last_name = models.CharField(verbose_name='Фамилия',
                                 max_length=255,
                                 null=True, blank=True)
    middle_name = models.CharField(verbose_name='Отчество',
                                   max_length=255,
                                   null=True, blank=True)
    email = models.EmailField(verbose_name='Почта',
                              max_length=60, unique=True)
    avatar = models.ImageField(verbose_name='Фото',
                               upload_to='User',
                               null=True, blank=True)
    date_of_birth = models.DateField(verbose_name='Дата рождения',
                                     default=date.today)
    country = models.CharField(verbose_name='Страна',
                               max_length=255,
                               null=True, blank=True)
    city = models.CharField(verbose_name='Город',
                            max_length=255,
                            null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.last_name}, {self.email}'


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Account(models.Model):
    balance = models.DecimalField(default=0, max_digits=9, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Счет'
        verbose_name_plural = 'Счета'

    def __str__(self):
        return f'{self.id} of {self.user}'


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
