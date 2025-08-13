from django.db import models

from django.utils import timezone
from django.urls import reverse

from config import settings


class Client(models.Model):
    email = models.EmailField(verbose_name='Почта')
    full_name = models.CharField(max_length=150, verbose_name='Ф. И. О.')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='clients',
        db_index=True,
    )

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'получатель'
        verbose_name_plural = 'получатели'
        ordering = ['full_name']
        constraints = [
            models.UniqueConstraint(fields=['owner', 'email'], name='uniq_owner_email'),
        ]
        permissions = [
            ("view_all_clients", "Может просматривать всех клиентов"),
        ]


class Message(models.Model):
    topic = models.CharField(max_length=150, verbose_name='Тема письма')
    body = models.TextField(verbose_name='Текст письма')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages',
        db_index=True
    )

    def __str__(self):
        return self.topic

    class Meta:
        verbose_name = 'письмо'
        verbose_name_plural = 'письма'
        ordering = ['topic']
        permissions = (
            ("view_all_messages", "Может просматривать все сообщения"),
        )


class Mailing(models.Model):
    class Status(models.TextChoices):
        CREATED = 'created', 'Создана'
        RUNNING = 'running', 'Запущена'
        FINISHED = 'finished', 'Завершена'

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CREATED,
        db_index=True,
        verbose_name='Статус',
    )
    start_time = models.DateTimeField(verbose_name='Время запуска')
    end_time = models.DateTimeField(verbose_name='Время окончания')
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        verbose_name='Сообщение',
        related_name='mailings'
    )
    clients = models.ManyToManyField(
        Client,
        blank=True,
        verbose_name='Получатели',
        related_name='mailings'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mailings',
        db_index=True,
    )

    def __str__(self):
        return f'Рассылка #{self.pk}'

    class Meta:
        verbose_name = 'рассылка'
        verbose_name_plural = 'рассылки'
        ordering = ['start_time']
        permissions = [
            ("view_all_mailings", "Может просматривать все рассылки"),
        ]


class Attempt(models.Model):
    class Status(models.TextChoices):
        SUCCEEDED = 'succeeded', 'Успешно'
        FAILED = 'failed', 'Не успешно'

    date = models.DateTimeField(default=timezone.now, verbose_name='Время попытки')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        db_index=True,
        verbose_name='Статус',
    )
    reply = models.TextField(blank=True, verbose_name='Ответ почтового сервера')
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        verbose_name='Рассылка',
        related_name='attempts'
    )

    def __str__(self):
        return f'{self.get_status_display()} — {self.date:%Y-%m-%d %H:%M}'

    def get_absolute_url(self):
        return reverse("mailings:attempt_detail", kwargs={"pk": self.pk})

    class Meta:
        verbose_name = 'попытка'
        verbose_name_plural = 'попытки'
        ordering = ['-date']
        permissions = [
            ("view_all_attempts", "Может просматривать все попытки"),
        ]
