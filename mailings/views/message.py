from ..forms import MessageForm
from ..models import Message
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailings/message_list.html'
    context_object_name = 'messages'

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm('mailings.view_all_messages'):
            return qs
        return qs.filter(owner=self.request.user)


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = 'mailings/message_detail.html'
    context_object_name = 'message'

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm('mailings.view_all_messages'):
            return qs
        return qs.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    template_name = 'mailings/message_form.html'
    form_class = MessageForm
    context_object_name = 'message'

    def get_success_url(self):
        return reverse('mailings:message_detail', kwargs={'pk': self.object.pk})


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    template_name = 'mailings/message_form.html'
    form_class = MessageForm
    context_object_name = 'message'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse('mailings:message_detail', kwargs={'pk': self.object.pk})


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'mailings/message_confirm_delete.html'
    success_url = reverse_lazy('mailings:message_list')
    context_object_name = 'message'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)
