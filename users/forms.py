from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from users.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Форма регистрации нового пользователя.

    Особенности:
    - проверяет уникальность email,
    - сохраняет пользователя с неактивным статусом (is_active=False),
      чтобы активация происходила через подтверждение по email.
    """
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'username', 'phone', 'country', 'avatar')

    def clean_email(self):
        """Валидирует email: приводит к нижнему регистру и проверяет уникальность."""
        email = self.cleaned_data['email'].strip().lower()
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError(_("Пользователь с таким email уже существует."))
        return email

    def save(self, commit=True):
        """Сохраняет пользователя с флагом is_active=False."""
        user = super().save(commit=False)
        user.is_active = False
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Форма аутентификации по email и паролю.

    Заменяет стандартное поле username на email.
    """
    username = forms.EmailField(label="Email")

    def clean(self):
        """Проверяет корректность email и пароля через authenticate."""
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Неверный email или пароль")
        return self.cleaned_data


class ProfileForm(forms.ModelForm):
    """Форма профиля пользователя.

    Позволяет редактировать имя, телефон, страну и аватар.
    Поле email недоступно для редактирования.
    """
    class Meta:
        model = CustomUser
        fields = ["username", "email", "phone", "country", "avatar"]

    def __init__(self, *args, **kwargs):
        """Делаем email нередактируемым (disabled + readonly)."""
        super().__init__(*args, **kwargs)
        self.fields["email"].disabled = True
        self.fields["email"].widget.attrs.update({"readonly": "readonly"})
