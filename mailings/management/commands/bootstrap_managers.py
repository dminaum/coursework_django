from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

MAILINGS_PERMS = [
    "view_all_clients",
    "view_all_mailings",
    "view_all_attempts",
    "view_all_messages",
]

AUTH_PERMS = [
    "view_user",
]


class Command(BaseCommand):
    help = "Создаёт группу «Менеджеры» и назначает ей нужные права"

    def handle(self, *args, **kwargs):
        group, _ = Group.objects.get_or_create(name="Менеджеры")

        perms_qs = Permission.objects.filter(
            codename__in=MAILINGS_PERMS + AUTH_PERMS
        )
        before = set(group.permissions.values_list("codename", flat=True))

        group.permissions.add(*perms_qs)
        group.save()

        after = set(group.permissions.values_list("codename", flat=True))
        added = sorted(after - before)

        if added:
            self.stdout.write(self.style.SUCCESS(
                "Добавлены права в «Менеджеры»: " + ", ".join(added)
            ))
        else:
            self.stdout.write("Права уже были назначены — изменений нет.")
