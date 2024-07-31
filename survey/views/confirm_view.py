from django.views.generic import TemplateView
from survey.utility.diagnostic import Diagnostic_Analyze
from survey.models import Response
from django.core.cache import cache

class ConfirmView(TemplateView):
    template_name = "survey/confirm.html"

    def get(self,request, *args, **kwargs):
        context = self.get_context_data(request, **kwargs)
        return self.render_to_response(context)

    def get_context_data(self,request, **kwargs):
        context = super().get_context_data(**kwargs)
        context["uuid"] = str(kwargs["uuid"])
        context["response"] = Response.objects.get(interview_uuid=context["uuid"])
        context["survey"] = context["response"].survey

        control_question_key = "control_question_{}_{}".format(request.user, context["response"].survey.name)
        control_question_ = int(cache.get(control_question_key))
        if control_question_ >=1:
            msg, diagnostic_result_msg =(
                "私たちは、あなたが他の人とは違う存在になるために、意図的に反対の選択肢を選んでいることを見抜いた。 \n\n 申し訳ございませんが、あなたのアカウントは停止され、あなたの回答はデータから削除されました。 ",
                "  "
            )
        else:
            msg, diagnostic_result_msg,majority_rate_r, correctness_rate_r = Diagnostic_Analyze(int(kwargs["majority_rate"]), int(kwargs["correctness_rate"]), kwargs)
        context["msg"] = msg
        context["diagnostic_result_msg"] = diagnostic_result_msg
        context["majority_rate_r"] = majority_rate_r*100
        context["correctness_rate_r"] = correctness_rate_r*100

        return context
