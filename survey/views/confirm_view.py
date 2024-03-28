from django.views.generic import TemplateView
from survey.utility.diagnostic import Diagnostic_Analyze
from survey.models import Response


class ConfirmView(TemplateView):
    template_name = "survey/confirm.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["uuid"] = str(kwargs["uuid"])
        context["response"] = Response.objects.get(interview_uuid=context["uuid"])
        context["survey"] = context["response"].survey
        msg, diagnostic_result_msg = Diagnostic_Analyze(int(kwargs["majority_rate"]), int(kwargs["correctness_rate"]), kwargs)
        context["msg"] = msg
        context["diagnostic_result_msg"] = diagnostic_result_msg
        return context
