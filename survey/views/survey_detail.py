import logging
import random

from django.conf import settings
from django.shortcuts import redirect, render, reverse
from django.views.generic import View

from survey.decorators import survey_available
from survey.forms import ResponseForm
from survey.models import Answer, Category, Question, Response, Survey
from survey.utility.diagnostic import Diagnostic_Analyze

LOGGER = logging.getLogger(__name__)

class SurveyDetail(View):
    @survey_available
    def get(self, request, *args, **kwargs):
        survey = kwargs.get("survey")
        step = kwargs.get("step", 0)
        session_key = "survey_{}".format(kwargs["id"])
        diagnostic_session_key = "diagnostic_{}_{}".format(request.user, kwargs["survey"].name)

        if step == 0:
            try:
                temp = request.session[diagnostic_session_key]
            except:
                pass
            else:
                del request.session[diagnostic_session_key]

            try:
                temp = request.session[session_key]
            except:
                pass
            else:
                del request.session[session_key]

        if survey.template is not None and len(survey.template) > 4:
            template_name = survey.template
        else:
            if survey.is_all_in_one_page():
                template_name = "survey/one_page_survey.html"
            else:
                template_name = "survey/survey.html"
        if survey.need_logged_user and not request.user.is_authenticated:
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")

        session_random_list = request.session.get("session_random_list",False)
        if not session_random_list:
            request.session["session_random_list"] = {}
            for i in range(1,100):
                request.session["session_random_list"][str(i)] = random.randint(100, 9999999)
                session_random_list = request.session.get("session_random_list")

        # -------------------------------------------------------------------
        form = ResponseForm(survey=survey, user=request.user, step=step, requests=request, session_random_list=session_random_list)
        categories = form.current_categories()

        asset_context = {
            # If any of the widgets of the current form has a "date" class, flatpickr will be loaded into the template
            "flatpickr": any(field.widget.attrs.get("class") == "date" for _, field in form.fields.items())
        }
        context = {
            "response_form": form,
            "survey": survey,
            "categories": categories,
            "step": step,
            "asset_context": asset_context,
            "user_logged": request.user.is_authenticated,
        }
        return render(request, template_name, context)

    @survey_available
    def post(self, request, *args, **kwargs):
        survey = kwargs.get("survey")
        if survey.need_logged_user and not request.user.is_authenticated:
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")
        session_random_list = request.session.get("session_random_list",False)
        if not session_random_list:
            request.session["session_random_list"] = {}
            for i in range(1,100):
                request.session["session_random_list"][str(i)] = random.randint(100, 9999999)
            session_random_list = request.session.get("session_random_list")

        form = ResponseForm(request.POST, survey=survey, user=request.user, step=kwargs.get("step", 0), requests=request, session_random_list=session_random_list)
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

    def Merge(self, dict1, dict2):
        res = {**dict1, **dict2}
        return res


    def treat_valid_form(self, form, kwargs, request, survey):
        diagnostic_session_key = "diagnostic_{}_{}".format(request.user, kwargs["survey"].name)
        if diagnostic_session_key not in request.session:
            request.session[diagnostic_session_key] = {}
            request.session.modified = True
            request.session[diagnostic_session_key]["Majority_Rate"] = "0"
            request.session.modified = True
            request.session[diagnostic_session_key]["Correctness_Rate"] = "0"
            request.session.modified = True

        majority_rate = int(request.session[diagnostic_session_key]["Majority_Rate"])
        correctness_rate = int(request.session[diagnostic_session_key]["Correctness_Rate"])

        session_key = "survey_{}".format(kwargs["id"])
        for field_name, field_value in list(form.cleaned_data.items()):
            if field_name.startswith("question_"):
                q_id = int(field_name.split("_")[1])
                question = Question.objects.get(pk=q_id)
                break
        if session_key not in request.session:
            request.session[session_key] = {}
        for key, value in list(form.cleaned_data.items()):
            # print("-----------------------------------------------")
            # print("key:",key)
            # print("value:",value)
            request.session[session_key][key] = value
            request.session.modified = True

            if question.subsidiary_type == "majority_minority":
                if key.startswith("question_") and not key.startswith("question_subsidiary_"):
                    choice = value
                if key.startswith("question_subsidiary_"):
                    if value == "majority":
                        request.session[diagnostic_session_key]["Majority_Rate"] = str(majority_rate + 1)
                        request.session.modified = True
                        if question.majority_choices == choice:
                            request.session[diagnostic_session_key]["Correctness_Rate"] = str(correctness_rate + 1)
                            request.session.modified = True
                    elif value == "minority":
                        if question.majority_choices != choice:
                            request.session[diagnostic_session_key]["Correctness_Rate"] = str(correctness_rate + 1)
                            request.session.modified = True

            elif question.subsidiary_type == "certainty_degree":
                pass
        # if settings.DISPLAY_SURVEY_QUESTIONNAIRE_INFORMATION:
        #     print(" ------------------------------------------------------------ ")
        #     print("request.session[diagnostic_session_key][Correctness_Rate]",
        #           request.session[diagnostic_session_key]["Correctness_Rate"])
        #     print("request.session[diagnostic_session_key][Majority_Rate]",
        #           request.session[diagnostic_session_key]["Majority_Rate"])
        #     print(" -------- ")
        next_url = form.next_step_url()
        response = None
        if survey.is_all_in_one_page():
            # 如果是单页调查问卷，那么提交意味着答题结束
            response = form.save()
        else:
            # when it's the last step
            if not form.has_next_step():
                # 如果没有next_step,那么意味着答题结束
                save_form = ResponseForm(request.session[session_key], survey=survey, user=request.user, requests=request)
                if save_form.is_valid():
                    response = save_form.save()
                else:
                    LOGGER.warning("A step of the multipage form failed but should have been discovered before.")
        # if there is a next step
        if next_url is not None:
            step = int(kwargs.get("step", 0)) + 1
            if step % survey.diagnosis_stages_qs_num != 0:
                context = self.result_pre_question(form, next_url, request)
                template_name = "survey/result_pre_question.html"
                return render(request, template_name, context)
            elif step % survey.diagnosis_stages_qs_num == 0:
                context1 = self.result_pre_question(form, next_url, request)
                context2 = self.Diagnostic_Result(form, next_url, request, kwargs)
                context = self.Merge(context1, context2)
                # print("---------------->context:",context)
                template_name = "survey/result_pre_question.html"
                return render(request, template_name, context)

        # todo 是不是需要同时删除 session_random_order
        if response is None:
            return redirect(reverse("survey-list"))
        next_ = request.session.get("next", None)
        if next_ is not None:
            if "next" in request.session:
                del request.session["next"]
            return redirect(next_)

        diagnostic_session_key = "diagnostic_{}_{}".format(request.user, kwargs["survey"].name)
        majority_rate = int(request.session[diagnostic_session_key]["Majority_Rate"])
        correctness_rate = int(request.session[diagnostic_session_key]["Correctness_Rate"])
        # return redirect(survey.redirect_url or "survey-confirmation", uuid=response.interview_uuid)
        return redirect("survey-confirmation", uuid=response.interview_uuid, majority_rate=majority_rate, correctness_rate=correctness_rate)

    def Diagnostic_Result(self, form, next_url, request, kwargs):

        context = self.result_pre_question(form, next_url, request)
        diagnostic_session_key = "diagnostic_{}_{}".format(request.user, kwargs["survey"].name)
        majority_rate = int(request.session[diagnostic_session_key]["Majority_Rate"])
        correctness_rate = int(request.session[diagnostic_session_key]["Correctness_Rate"])

        msg, diagnostic_result_msg = Diagnostic_Analyze(majority_rate, correctness_rate, kwargs)
        context["diagnostic_result"] = diagnostic_result_msg
        context["msg_diagnostic"] = msg
        return context


    def result_pre_question(self, form, next_url, request):
        # not_enough = True
        # msg=""
        for field_name, field_value in list(form.cleaned_data.items()):
            if field_name.startswith("question_") and not field_name.startswith("question_subsidiary_"):
                choice = field_value
            if field_name.startswith("question_subsidiary_"):
                qqqq = field_value
                pk = int(field_name.split("_")[2])
                question = Question.objects.get(pk=pk)
                #sam-todo 因为每次回答都更新最多数的回答，所以这里更改判断条件

                if question.number_of_responses < question.survey.diagnostic_page_indexing:
                    not_enough = True
                    msg = "あなたの回答の結果はまだ十分に回答が集まっていないため、診断結果は後ほどまたログインして確かめてください."
                else:
                    not_enough = False

                    if question.subsidiary_type == "majority_minority":
                        if question.majority_choices == choice:
                            if qqqq == "majority":
                                msg = "正解、あなたの回答は多数派"
                            else:
                                msg = "不正解、あなたの回答は少数派"
                        else:
                            if qqqq == "minority":
                                msg = "正解、あなたの回答は少数派"
                            else:
                                msg = "不正解、あなたの回答は多数派"
            else:
                not_enough = True
                msg = "Error"

        context = {
            "next_url": next_url,
            "not_enough": not_enough,
            "msg": msg,

        }

        return context