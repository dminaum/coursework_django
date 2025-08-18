from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from ..models import Attempt


class AttemptView(LoginRequiredMixin, ListView):
    """Список попыток отправки сообщений.

    Отображает все попытки рассылок с возможностью фильтрации
    по пользователю, рассылке и статусу.
    """
    model = Attempt
    template_name = 'mailings/attempts_list.html'
    context_object_name = 'attempts'

    def get_queryset(self):
        """Возвращает выборку попыток с фильтрацией.

        - Если у пользователя есть право 'view_all_attempts',
          возвращаются все попытки.
        - Иначе — только попытки рассылок текущего пользователя.
        - Дополнительно можно фильтровать по ID рассылки (pk)
          и по статусу (успешно/неуспешно).
        """
        qs = (Attempt.objects
              .select_related('mailing')
              .order_by('-date'))
        if not self.request.user.has_perm('mailings.view_all_attempts'):
            qs = qs.filter(mailing__owner=self.request.user)

        mailing_id = self.kwargs.get('pk')
        if mailing_id:
            qs = qs.filter(mailing_id=mailing_id)
        status = self.request.GET.get('status')
        if status in [Attempt.Status.SUCCEEDED, Attempt.Status.FAILED]:
            qs = qs.filter(status=status)
        return qs


class AttemptDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о попытке отправки."""
    model = Attempt
    template_name = 'mailings/attempt_detail.html'
    context_object_name = 'attempt'

    def get_queryset(self):
        """Возвращает выборку попыток с учётом прав доступа.

        - Если у пользователя есть право 'view_all_attempts',
          возвращаются все попытки.
        - Иначе — только попытки рассылок текущего пользователя.
        """
        qs = super().get_queryset().select_related('mailing')
        if self.request.user.has_perm('mailings.view_all_attempts'):
            return qs
        return qs.filter(mailing__owner=self.request.user)

    def get_context_data(self, **kwargs):
        """Добавляет в контекст человекочитаемое название статуса."""
        ctx = super().get_context_data(**kwargs)
        ctx["status_display"] = self.object.get_status_display()
        return ctx
