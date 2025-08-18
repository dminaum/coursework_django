from ..forms import ClientForm
from ..models import Client
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin


class ClientListView(LoginRequiredMixin, ListView):
    """Список клиентов.

    Отображает клиентов текущего пользователя.
    Менеджеры видят всех клиентов.
    """
    model = Client
    template_name = 'mailings/client_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        """Фильтрует список клиентов.

        Возвращает всех клиентов, если у пользователя есть
        право 'view_all_clients'. В противном случае — только
        клиентов текущего пользователя.
        """
        qs = super().get_queryset()
        if self.request.user.has_perm('mailings.view_all_clients'):
            return qs
        return qs.filter(owner=self.request.user)


class ClientDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о клиенте."""
    model = Client
    template_name = 'mailings/client_detail.html'
    context_object_name = 'client'

    def get_queryset(self):
        """Фильтрует доступ к клиенту.

        Возвращает всех клиентов, если у пользователя есть
        право 'view_all_clients'. Иначе — только клиентов,
        принадлежащих текущему пользователю.
        """
        qs = super().get_queryset()
        if self.request.user.has_perm('mailings.view_all_clients'):
            return qs
        return qs.filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    """Создание нового клиента.

    Автоматически назначает текущего пользователя владельцем.
    """
    model = Client
    template_name = 'mailings/client_form.html'
    form_class = ClientForm
    context_object_name = 'client'

    def form_valid(self, form):
        """Сохраняет клиента с указанием владельца.

        Перед сохранением объекту назначается текущий пользователь.
        """
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Возвращает URL детальной страницы клиента после создания."""
        return reverse('mailings:client_detail', kwargs={'pk': self.object.pk})


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование клиента.

    Доступно только для владельца клиента.
    """
    model = Client
    template_name = 'mailings/client_form.html'
    form_class = ClientForm
    context_object_name = 'client'

    def get_queryset(self):
        """Ограничивает выборку клиентами текущего пользователя."""
        return super().get_queryset().filter(owner=self.request.user)

    def get_success_url(self):
        """Возвращает URL детальной страницы клиента после обновления."""
        return reverse('mailings:client_detail', kwargs={'pk': self.object.pk})


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление клиента.

    Доступно только для владельца клиента.
    """
    model = Client
    template_name = 'mailings/client_confirm_delete.html'
    success_url = reverse_lazy('mailings:client_list')
    context_object_name = 'client'

    def get_queryset(self):
        """Ограничивает удаление клиентами текущего пользователя."""
        return super().get_queryset().filter(owner=self.request.user)
