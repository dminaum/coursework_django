from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Кастомная модель пользователя.

    Отличия от стандартной:
    - используется email как уникальный идентификатор для входа (USERNAME_FIELD),
    - добавлены поля: аватар, телефон и страна,
    - username остаётся обязательным дополнительным полем.

    Поля:
        email (EmailField): уникальный email, используется для аутентификации.
        avatar (ImageField): изображение профиля, сохраняется в папку 'avatars/'.
        phone (CharField): телефонный номер пользователя.
        country (CharField): страна пользователя.
    """
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        """Возвращает строковое представление пользователя — email."""
        return self.email
