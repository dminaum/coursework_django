from django.conf import settings
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileForm
from .tokens import activation_token_generator

User = get_user_model()


class RegisterView(CreateView):
    """Регистрация нового пользователя.

    - Создаёт пользователя с флагом is_active=False.
    - Отправляет письмо с активационной ссылкой.
    """
    template_name = "users/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("users:signup_done")

    def form_valid(self, form):
        """Сохраняет пользователя и отправляет письмо для активации."""
        user = form.save(commit=False)
        if user.is_active:
            user.is_active = False
        user.save()
        self._send_activation_email(user)
        self.object = user
        return redirect(self.get_success_url())

    def _send_activation_email(self, user):
        """Формирует и отправляет письмо с активационной ссылкой."""
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = activation_token_generator.make_token(user)
        activation_link = self.request.build_absolute_uri(
            reverse("users:activate", args=[uidb64, token])
        )
        subject = "Подтвердите регистрацию"
        message = (
            f"Здравствуйте, {user.username or user.email}!\n\n"
            f"Для активации аккаунта перейдите по ссылке:\n{activation_link}\n\n"
            f"Если вы не регистрировались, просто проигнорируйте это письмо."
        )
        send_mail(
            subject,
            message,
            getattr(settings, "DEFAULT_FROM_EMAIL", None),
            [user.email],
            fail_silently=False,
        )


class ActivateView(View):
    """Активация пользователя по токену из письма."""

    template_ok = "users/activated.html"
    template_fail = "users/activation_failed.html"

    def get(self, request, uidb64, token):
        """Проверяет токен и активирует пользователя."""
        user = self._get_user_from_uid(uidb64)
        if user and activation_token_generator.check_token(user, token):
            if not user.is_active:
                user.is_active = True
                user.save(update_fields=["is_active"])
            # опционально: login(request, user)
            return render(request, self.template_ok, {"user": user})
        return render(request, self.template_fail, status=400)

    @staticmethod
    def _get_user_from_uid(uidb64):
        """Получает пользователя из закодированного uid."""
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            return User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None


class CustomLoginView(LoginView):
    """Авторизация пользователя по email и паролю."""
    template_name = "users/login.html"
    authentication_form = CustomAuthenticationForm


def simple_logout(request):
    """Выход пользователя из системы и редирект на страницу входа."""
    logout(request)
    return redirect("users:login")


class ProfileView(LoginRequiredMixin, DetailView):
    """Просмотр профиля текущего пользователя."""
    model = User
    template_name = "users/profile_detail.html"
    context_object_name = "user_obj"

    def get_object(self, queryset=None):
        """Возвращает текущего пользователя."""
        return self.request.user


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля текущего пользователя."""
    model = User
    form_class = ProfileForm
    template_name = "users/profile_form.html"
    context_object_name = "user_obj"

    def get_object(self, queryset=None):
        """Возвращает текущего пользователя."""
        return self.request.user

    def get_success_url(self):
        """После обновления профиля выполняется редирект на детальную страницу профиля."""
        return reverse_lazy("users:profile")
