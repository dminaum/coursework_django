from django.core.mail import send_mail
from django.utils import timezone
from .models import Attempt, Mailing


def send_mailing_now(mailing: Mailing) -> dict:
    mailing.refresh_from_db()
    stats = {"total": 0, "ok": 0, "failed": 0}

    if mailing.status != Mailing.Status.RUNNING:
        mailing.status = Mailing.Status.RUNNING
        mailing.save(update_fields=["status"])

    subject = mailing.message.topic
    body = mailing.message.body

    from_email = None

    for client in mailing.clients.all():
        stats["total"] += 1
        try:
            sent = send_mail(
                subject=subject,
                message=body,
                from_email=from_email,
                recipient_list=[client.email],
                fail_silently=False,
            )
            if sent == 1:
                Attempt.objects.create(
                    mailing=mailing,
                    status=Attempt.Status.SUCCEEDED,
                    reply="OK",
                    date=timezone.now(),
                )
                stats["ok"] += 1
            else:
                Attempt.objects.create(
                    mailing=mailing,
                    status=Attempt.Status.FAILED,
                    reply="Неизвестный результат: send_mail вернул 0",
                    date=timezone.now(),
                )
                stats["failed"] += 1
        except Exception as e:
            Attempt.objects.create(
                mailing=mailing,
                status=Attempt.Status.FAILED,
                reply=str(e),
                date=timezone.now(),
            )
            stats["failed"] += 1

    # пометим завершение
    mailing.status = Mailing.Status.FINISHED
    mailing.save(update_fields=["status"])

    return stats
