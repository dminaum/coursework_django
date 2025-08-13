from django.views.generic import TemplateView
from .views import RegisterView, ActivateView, CustomLoginView, simple_logout, ProfileView, ProfileUpdateView
from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

app_name = 'users'


urlpatterns = [
    path("signup/", RegisterView.as_view(), name="signup"),
    path("signup/done/", TemplateView.as_view(template_name="users/signup_done.html"), name="signup_done"),
    path("activate/<uidb64>/<token>/", ActivateView.as_view(), name="activate"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", simple_logout, name="logout"),
    path("password-reset/", auth_views.PasswordResetView.as_view(
        template_name="users/password_reset_form.html",
        email_template_name="users/password_reset_email.html",
        subject_template_name="users/password_reset_subject.txt",
        success_url=reverse_lazy("users:password_reset_done"),
    ), name="password_reset"),

    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="users/password_reset_done.html",
    ), name="password_reset_done"),

    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="users/password_reset_confirm.html",
        success_url=reverse_lazy("users:password_reset_complete"),
    ), name="password_reset_confirm"),

    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="users/password_reset_complete.html",
    ), name="password_reset_complete"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/edit/", ProfileUpdateView.as_view(), name="profile_edit"),
]
