from datetime import date
from django.contrib.auth.mixins import PermissionRequiredMixin

from django.views.generic import TemplateView

from survey.models import Survey


class IndexView(PermissionRequiredMixin,TemplateView):
    template_name = "survey/list.html"
    permission_required = ('survey.participant','survey.experimenter')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        surveys = Survey.objects.filter(
            is_published=True, expire_date__gte=date.today(), publish_date__lte=date.today()
        )
        if not self.request.user.is_authenticated:
            surveys = surveys.filter(need_logged_user=True)
        context["surveys"] = surveys
        return context
