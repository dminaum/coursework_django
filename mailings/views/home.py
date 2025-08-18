from django.views.generic import TemplateView
from ..models import Mailing, Client
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, cache_control


@method_decorator([cache_control(public=True, max_age=120), cache_page(120)], name="dispatch")
class HomeView(TemplateView):
    """Главная страница сервиса рассылок.

    Отображает общую статистику:
    - количество всех рассылок,
    - количество активных (запущенных) рассылок,
    - количество уникальных клиентов.
    Кэшируется на 120 секунд.
    """
    template_name = 'mailings/home.html'

    def get_context_data(self, **kwargs):
        """Добавляет статистику в контекст шаблона."""
        context = super().get_context_data(**kwargs)

        context['total_mailings'] = Mailing.objects.count()
        context['active_mailings'] = Mailing.objects.filter(status=Mailing.Status.RUNNING).count()
        context['unique_clients'] = Client.objects.values('email').distinct().count()

        return context
