from ..forms import MessageForm
from ..models import Message
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailings/message_list.html'
    context_object_name = 'messages'
    paginate_by = 20
    ordering = ('-id',)

    def get_queryset(self):
        qs = super().get_queryset().select_related('owner')
        u = self.request.user
        if u.has_perm('mailings.view_all_messages'):
            return qs
        return qs.filter(owner=u)


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = 'mailings/message_detail.html'
    context_object_name = 'message'

    def get_queryset(self):
        qs = super().get_queryset().select_related('owner')
        u = self.request.user
        if u.has_perm('mailings.view_all_messages'):
            return qs
        return qs.filter(owner=u)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    template_name = 'mailings/message_form.html'
    form_class = MessageForm
    context_object_name = 'message'

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        self.object = obj
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('mailings:message_detail', kwargs={'pk': self.object.pk})


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    template_name = 'mailings/message_form.html'
    form_class = MessageForm
    context_object_name = 'message'

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)

    def get_success_url(self):
        return reverse('mailings:message_detail', kwargs={'pk': self.object.pk})


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'mailings/message_confirm_delete.html'
    success_url = reverse_lazy('mailings:message_list')
    context_object_name = 'message'

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)
