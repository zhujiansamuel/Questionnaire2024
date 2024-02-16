import logging
import random

from django.conf import settings
from django.shortcuts import redirect, render, reverse
from django.views.generic import View

from survey.decorators import survey_available
from survey.forms import ResponseForm
from survey.models import Answer, Category, Question, Response, Survey

LOGGER = logging.getLogger(__name__)



class SurveyDetail(View):
    # 这里是问题显示的后台逻辑
    # 对应着两个url，分别是首个问题和之后的问题
    # sam-todo 1
    # 每个问题后的结果提示
    # 每N个问题时候的分析
    # 每个类别取L个问题
    # 回答过的问题不在回答
    #
    @survey_available
    def get(self, request, *args, **kwargs):
        survey = kwargs.get("survey")
        step = kwargs.get("step", 0)
        if survey.template is not None and len(survey.template) > 4:
            template_name = survey.template
        else:
            if survey.is_all_in_one_page():
                template_name = "survey/one_page_survey.html"
            else:
                template_name = "survey/survey.html"
        if survey.need_logged_user and not request.user.is_authenticated:
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")
        # -------------------------------------------------------------------
        form = ResponseForm(survey=survey, user=request.user, step=step)
        categories = form.current_categories()

        asset_context = {
            # If any of the widgets of the current form has a "date" class, flatpickr will be loaded into the template
            "flatpickr": any(field.widget.attrs.get("class") == "date" for _, field in form.fields.items())
        }
        context = {
            # ->
            "response_form": form,
            "survey": survey,
            "categories": categories,
            "step": step,
            "asset_context": asset_context,
        }

        return render(request, template_name, context)

    @survey_available
    def post(self, request, *args, **kwargs):
        # 添加结果页面，考虑增加逻辑
        survey = kwargs.get("survey")
        if survey.need_logged_user and not request.user.is_authenticated:
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")

        form = ResponseForm(request.POST, survey=survey, user=request.user, step=kwargs.get("step", 0))
        categories = form.current_categories()

        if not survey.editable_answers and form.response is not None:
            LOGGER.info("Redirects to survey list after trying to edit non editable answer.")
            return redirect(reverse("survey-list"))
        context = {"response_form": form, "survey": survey, "categories": categories}
        if form.is_valid():
            return self.treat_valid_form(form, kwargs, request, survey)
        return self.handle_invalid_form(context, form, request, survey)

    @staticmethod
    def handle_invalid_form(context, form, request, survey):
        LOGGER.info("Non valid form: <%s>", form)
        if survey.template is not None and len(survey.template) > 4:
            template_name = survey.template
        else:
            if survey.is_all_in_one_page():
                template_name = "survey/one_page_survey.html"
            else:
                template_name = "survey/survey.html"
        return render(request, template_name, context)

    def treat_valid_form(self, form, kwargs, request, survey):
        session_key = "survey_{}".format(kwargs["id"])
        if session_key not in request.session:
            request.session[session_key] = {}
        for key, value in list(form.cleaned_data.items()):
            request.session[session_key][key] = value
            request.session.modified = True
        next_url = form.next_step_url()
        response = None
        if survey.is_all_in_one_page():
            response = form.save()
        else:
            # when it's the last step
            if not form.has_next_step():
                save_form = ResponseForm(request.session[session_key], survey=survey, user=request.user)
                if save_form.is_valid():
                    response = save_form.save()
                else:
                    LOGGER.warning("A step of the multipage form failed but should have been discovered before.")
        # if there is a next step
        if next_url is not None:
            context = self.result_pre_question(form, next_url)
            template_name = "survey/result_pre_question.html"
            return render(request, template_name, context)

        del request.session[session_key]
        if response is None:
            return redirect(reverse("survey-list"))
        next_ = request.session.get("next", None)
        if next_ is not None:
            if "next" in request.session:
                del request.session["next"]
            return redirect(next_)
        return redirect(survey.redirect_url or "survey-confirmation", uuid=response.interview_uuid)



    def result_pre_question(self,form,next_url):
        for field_name, field_value in list(form.cleaned_data.items()):
            if field_name.startswith("question_subsidiary_"):
                qqqq = field_value
                pk = int(field_name.split("_")[2])
                question = Question.objects.get(pk=pk)
                if question.majority_choices == "Null":
                    not_enough = True
                    msg = "There isn`t enough answers."
                else:
                    not_enough = False
                    if question.subsidiary_type == "majority_minority":
                        if question.majority_choices == "majority":
                            if qqqq == "majority":
                                msg = "正解、多数派ー多数派"
                            else:
                                msg = "不正解、多数派ー少数派"
                        else:
                            if qqqq == "minority":
                                msg = "正解、少数派ー少数派"
                            else:
                                msg = "不正解、少数派ー多数派"
            else:
                not_enough = True
                msg = "Error"

        context = {
            "next_url": next_url,
            "not_enough": not_enough,
            "msg": msg,

        }

        return context