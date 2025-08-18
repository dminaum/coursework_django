from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.shortcuts import get_object_or_404, redirect

from ..models import Mailing
from ..forms import MailingForm
from ..services import send_mailing_now


class MailingListView(LoginRequiredMixin, ListView):
    """Список рассылок.

    Отображает все рассылки текущего пользователя.
    Если у пользователя есть право 'view_all_mailings' —
    отображаются все рассылки в системе.
    """
    model = Mailing
    template_name = "mailings/mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        """Фильтрует рассылки по правам доступа."""
        qs = super().get_queryset()
        if self.request.user.has_perm('mailings.view_all_mailings'):
            return qs
        return qs.filter(owner=self.request.user)


class MailingDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о рассылке."""
    model = Mailing
    template_name = "mailings/mailing_detail.html"
    context_object_name = "mailing"

    def get_queryset(self):
        """Фильтрует доступ к рассылкам по владельцу и правам."""
        qs = super().get_queryset()
        if self.request.user.has_perm('mailings.view_all_mailings'):
            return qs
        return qs.filter(owner=self.request.user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    """Создание новой рассылки.

    При сохранении автоматически указывает текущего пользователя
    как владельца рассылки.
    """
    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_form.html"

    def get_form_kwargs(self):
        """Передаёт объект пользователя в форму для фильтрации клиентов/сообщений."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Сохраняет рассылку и назначает владельца."""
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        form.save_m2m()
        return super().form_valid(form)

    def get_success_url(self):
        """Возвращает URL детальной страницы после создания рассылки."""
        return reverse("mailings:mailing_detail", kwargs={"pk": self.object.pk})


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование рассылки.

    Доступно только владельцу рассылки.
    """
    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_form.html"

    def get_queryset(self):
        """Ограничивает выборку рассылками текущего пользователя."""
        return super().get_queryset().filter(owner=self.request.user)

    def get_form_kwargs(self):
        """Передаёт объект пользователя в форму для фильтрации клиентов/сообщений."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        """Возвращает URL детальной страницы после редактирования."""
        return reverse("mailings:mailing_detail", kwargs={"pk": self.object.pk})


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление рассылки.

    Доступно только владельцу рассылки.
    """
    model = Mailing
    template_name = "mailings/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailings:mailing_list")

    def get_queryset(self):
        """Ограничивает удаление рассылками текущего пользователя."""
        return super().get_queryset().filter(owner=self.request.user)


class MailingSendNowView(LoginRequiredMixin, View):
    """Ручной запуск рассылки.

    Отправляет все сообщения выбранной рассылки и выводит статистику
    (количество успешных и неуспешных отправок).
    """
    def post(self, request, pk):
        """Запускает рассылку и добавляет сообщение об успехе в интерфейс."""
        mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)
        stats = send_mailing_now(mailing)
        messages.success(
            request,
            f"Отправлено: {stats['ok']} из {stats['total']}. Ошибок: {stats['failed']}."
        )
        return redirect("mailings:mailing_detail", pk=mailing.pk)
