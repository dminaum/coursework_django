from django import forms
from .models import Client, Message, Mailing
from django.core.exceptions import ValidationError


class ClientForm(forms.ModelForm):
    """Форма для создания и редактирования клиентов.

    Переопределяет валидацию email для нормализации (строчные буквы).
    """
    class Meta:
        model = Client
        fields = ['email', 'full_name', 'comment']

    def clean_email(self):
        return self.cleaned_data['email'].strip().lower()


class MessageForm(forms.ModelForm):
    """Форма для создания и редактирования сообщений рассылки."""
    class Meta:
        model = Message
        fields = ['topic', 'body']


class MailingForm(forms.ModelForm):
    """Форма для создания и редактирования рассылок.

    Валидирует корректность дат (начало < конец).
    """
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"})
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"})
    )
    # ВАЖНО: по умолчанию — пустой queryset
    clients = forms.ModelMultipleChoiceField(
        queryset=Client.objects.none(),
        widget=forms.SelectMultiple(attrs={"size": 10})
    )

    class Meta:
        model = Mailing
        fields = ["start_time", "end_time", "message", "clients"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user is not None:
            self.fields['clients'].queryset = Client.objects.filter(owner=user)

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_time")
        end = cleaned.get("end_time")
        clients = cleaned.get("clients")

        if start and end and start >= end:
            self.add_error("end_time", "Время окончания должно быть позже времени запуска.")

        if clients is not None and clients.count() == 0:
            self.add_error("clients", "Выберите хотя бы одного получателя.")

        return cleaned

    def clean_clients(self):
        clients = self.cleaned_data.get('clients')
        if clients is None:
            return clients
        if hasattr(self, 'user') and self.user is not None:
            bad = clients.exclude(owner=self.user)
            if bad.exists():
                raise ValidationError("Нельзя выбирать клиентов, которые вам не принадлежат.")
        return clients
