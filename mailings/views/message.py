from ..forms import MessageForm
from ..models import Message
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect


class MessageListView(LoginRequiredMixin, ListView):
    """Список сообщений.

    Отображает сообщения текущего пользователя.
    Если есть право 'view_all_messages', показываются все сообщения.
    """
    model = Message
    template_name = 'mailings/message_list.html'
    context_object_name = 'messages'
    paginate_by = 20
    ordering = ('-id',)

    def get_queryset(self):
        """Фильтрует сообщения по владельцу и правам доступа."""
        qs = super().get_queryset().select_related('owner')
        u = self.request.user
        if u.has_perm('mailings.view_all_messages'):
            return qs
        return qs.filter(owner=u)


class MessageDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о сообщении."""
    model = Message
    template_name = 'mailings/message_detail.html'
    context_object_name = 'message'

    def get_queryset(self):
        """Фильтрует доступ к сообщениям по владельцу и правам."""
        qs = super().get_queryset().select_related('owner')
        u = self.request.user
        if u.has_perm('mailings.view_all_messages'):
            return qs
        return qs.filter(owner=u)


class MessageCreateView(LoginRequiredMixin, CreateView):
    """Создание нового сообщения.

    Автоматически назначает владельцем текущего пользователя.
    """
    model = Message
    template_name = 'mailings/message_form.html'
    form_class = MessageForm
    context_object_name = 'message'

    def form_valid(self, form):
        """Сохраняет сообщение и назначает владельца."""
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        self.object = obj
        return redirect(self.get_success_url())

    def get_success_url(self):
        """Возвращает URL детальной страницы после создания."""
        return reverse('mailings:message_detail', kwargs={'pk': self.object.pk})


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование сообщения.

    Доступно только владельцу.
    """
    model = Message
    template_name = 'mailings/message_form.html'
    form_class = MessageForm
    context_object_name = 'message'

    def get_queryset(self):
        """Ограничивает выборку сообщениями текущего пользователя."""
        return super().get_queryset().filter(owner=self.request.user)

    def get_success_url(self):
        """Возвращает URL детальной страницы после обновления."""
        return reverse('mailings:message_detail', kwargs={'pk': self.object.pk})


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление сообщения.

    Доступно только владельцу.
    """
    model = Message
    template_name = 'mailings/message_confirm_delete.html'
    success_url = reverse_lazy('mailings:message_list')
    context_object_name = 'message'

    def get_queryset(self):
        """Ограничивает удаление сообщениями текущего пользователя."""
        return super().get_queryset().filter(owner=self.request.user)
