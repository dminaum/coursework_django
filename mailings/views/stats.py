from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Count, Q
from ..models import Mailing, Client, Attempt
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, cache_control
from django.views.decorators.vary import vary_on_cookie


@method_decorator([vary_on_cookie, cache_control(private=True, max_age=60), cache_page(60)], name="dispatch")
class StatsView(LoginRequiredMixin, TemplateView):
    template_name = "mailings/stats.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        u = self.request.user

        ctx["total_mailings"] = Mailing.objects.filter(owner=u).count()
        ctx["active_mailings"] = Mailing.objects.filter(
            owner=u, status=Mailing.Status.RUNNING
        ).count()
        ctx["unique_clients"] = Client.objects.filter(owner=u).count()

        ctx["mailings_with_stats"] = (
            Mailing.objects.filter(owner=u)
            .select_related("message")
            .annotate(
                clients_count=Count("clients", distinct=True),
                success_count=Count(
                    "attempts",
                    filter=Q(attempts__status=Attempt.Status.SUCCEEDED),
                ),
                fail_count=Count(
                    "attempts",
                    filter=Q(attempts__status=Attempt.Status.FAILED),
                ),
            )
        )
        return ctx
