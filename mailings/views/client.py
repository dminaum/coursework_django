from ..forms import ClientForm
from ..models import Client
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'mailings/client_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm('mailings.view_all_clients'):
            return qs
        return qs.filter(owner=self.request.user)


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'mailings/client_detail.html'
    context_object_name = 'client'

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm('mailings.view_all_clients'):
            return qs
        return qs.filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    template_name = 'mailings/client_form.html'
    form_class = ClientForm
    context_object_name = 'client'

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('mailings:client_detail', kwargs={'pk': self.object.pk})


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    template_name = 'mailings/client_form.html'
    form_class = ClientForm
    context_object_name = 'client'

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)

    def get_success_url(self):
        return reverse('mailings:client_detail', kwargs={'pk': self.object.pk})


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = 'mailings/client_confirm_delete.html'
    success_url = reverse_lazy('mailings:client_list')
    context_object_name = 'client'

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)
