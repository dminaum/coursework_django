from django.core.management.base import BaseCommand, CommandError
from mailings.models import Mailing
from mailings.services import send_mailing_now


class Command(BaseCommand):
    help = "Отправить рассылку по требованию: python manage.py send_mailing <mailing_id>"

    def add_arguments(self, parser):
        parser.add_argument("mailing_id", type=int)

    def handle(self, *args, **options):
        mailing_id = options["mailing_id"]
        try:
            mailing = Mailing.objects.get(pk=mailing_id)
        except Mailing.DoesNotExist:
            raise CommandError(f"Рассылка #{mailing_id} не найдена")

        stats = send_mailing_now(mailing)
        self.stdout.write(self.style.SUCCESS(
            f"Готово. Отправлено {stats['ok']} из {stats['total']}, ошибок {stats['failed']}."
        ))
