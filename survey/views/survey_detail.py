import logging
import random

from django.conf import settings
from django.shortcuts import redirect, render, reverse
from django.views.generic import View
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from survey.decorators import survey_available
from survey.forms import ResponseForm
from survey.models import Answer, Category, Question, Response, Survey
from survey.utility.diagnostic import Diagnostic_Analyze
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib import messages

LOGGER = logging.getLogger(__name__)

class SurveyDetail(View):
    @method_decorator(never_cache)
    @survey_available
    def get(self, request, *args, **kwargs):
        survey = kwargs.get("survey")
        step = kwargs.get("step", 0)

        is_diagnostic_key = "is_diagnostic_{}_{}".format(request.user,survey)
        is_diagnostic_current_key = "current_key_diagnostic_{}".format(request.user)
        cache.set(is_diagnostic_current_key, is_diagnostic_key)
        diagnostic_status = cache.get(is_diagnostic_key)
        if not diagnostic_status:
            cache.set(is_diagnostic_key, 0)

        step_cache_key = "step_{}_{}".format(request.user,survey)
        current_key = "current_key_step_{}".format(request.user)
        cache.set(current_key, step_cache_key)
        step_database = cache.get(step_cache_key)

        print("step-form", step)
        print("step-database", step_database)
        if step_database is not None:
            if int(step_database) != int(step):
                messages.warning(request, "It appears that your experimental process has been interrupted. We will restart the experiment.")
                return redirect("home_n")
        elif step_database is None and int(step)!=0:
            messages.warning(request,
                             "It appears that your experimental process has been interrupted. We will restart the experiment.")
            return redirect("home_n")

        session_random_list = request.session.get("session_random_list",False)
        if not session_random_list:
            request.session["session_random_list"] = {}
            for i in range(1,50):
                request.session["session_random_list"][str(i)] = random.randint(100, 99999)
                session_random_list = request.session.get("session_random_list")


        if survey.template is not None and len(survey.template) > 4:
            template_name = survey.template
        else:
            if survey.is_all_in_one_page():
                template_name = "survey/one_page_survey.html"
            else:
                template_name = "survey/survey.html"
        if survey.need_logged_user and not request.user.is_authenticated:
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")

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

    @method_decorator(never_cache)
    @survey_available
    def post(self, request, *args, **kwargs):
        survey = kwargs.get("survey")
        if survey.need_logged_user and not request.user.is_authenticated:
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")
        session_random_list = request.session.get("session_random_list",False)
        form = ResponseForm(request.POST, survey=survey, user=request.user, step=kwargs.get("step", 0), requests=request, session_random_list=session_random_list)
        # print("BBBB-step:",kwargs.get("step", 0))
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

        is_diagnostic_key = "is_diagnostic_{}_{}".format(request.user,survey)
        diagnostic_status = int(cache.get(is_diagnostic_key))

        session_key = "survey_{}".format(kwargs["id"])
        for field_name, field_value in list(form.cleaned_data.items()):
            if field_name.startswith("question_"):
                q_id = int(field_name.split("_")[1])
                question = Question.objects.get(pk=q_id)
                if question.number_of_responses >= survey.diagnosis_stages_qs_num:
                    diagnostic_status += survey.diagnosis_stages_qs_num
                    cache.set(is_diagnostic_key,diagnostic_status)
                else:
                    diagnostic_status += question.number_of_responses
                    cache.set(is_diagnostic_key, diagnostic_status)
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
                # print(" ------------------------------------------------------------ ")
                # print("Question:",question)
                # print(" ------------------------------------------------------------ ")
                if key.startswith("question_") and not key.startswith("question_subsidiary_"):
                    choice = value
                    if question.category.block_type == "branch":
                        branch_mark_key = "branch_mark_{}_{}_{}".format(request.user, survey, question.category)
                        branch_mark = cache.get(branch_mark_key)
                        if branch_mark is None:
                            cache.set(branch_mark_key, question.get_choice_index(choice))


                    # print(" ------------------------------------------------------------ ")
                    # print("choice:",choice)
                    # print(" ------------------------------------------------------------ ")
                if key.startswith("question_subsidiary_"):
                    if value == "majority":
                        request.session[diagnostic_session_key]["Majority_Rate"] = str(majority_rate + 1)
                        request.session.modified = True
                        if question.majority_choices == choice:
                            request.session[diagnostic_session_key]["Correctness_Rate"] = str(correctness_rate + 1)
                            request.session.modified = True
                    elif value == "minority":
                        if question.majority_choices!="Null" and question.majority_choices != choice:
                            request.session[diagnostic_session_key]["Correctness_Rate"] = str(correctness_rate + 1)
                            request.session.modified = True

            elif question.subsidiary_type == "certainty_degree":
                pass
        if settings.DISPLAY_SURVEY_QUESTIONNAIRE_INFORMATION:
            print(" ------------------------------------------------------------ ")
            print("request.session[diagnostic_session_key][Correctness_Rate]",
                  request.session[diagnostic_session_key]["Correctness_Rate"])
            print("request.session[diagnostic_session_key][Majority_Rate]",
                  request.session[diagnostic_session_key]["Majority_Rate"])
            print(" -------- ")
        next_url = form.next_step_url()
        response = None
        session_random_list = request.session.get("session_random_list",False)
        # if not session_random_list:
        #     request.session["session_random_list"] = {}
        #     for i in range(1,50):
        #         request.session["session_random_list"][str(i)] = random.randint(100, 9999999)
        #     session_random_list = request.session.get("session_random_list")
        if survey.is_all_in_one_page():
            # 如果是单页调查问卷，那么提交意味着答题结束
            response = form.save()
        else:
            # when it's the last step
            if not form.has_next_step():
                # 如果没有next_step,那么意味着答题结束
                save_form = ResponseForm(request.session[session_key], survey=survey, user=request.user, requests=request, session_random_list=session_random_list)
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
        is_diagnostic_key = "is_diagnostic_{}_{}".format(request.user, form.survey)
        diagnostic_status = int(cache.get(is_diagnostic_key))
        if diagnostic_status < response.number_of_questions * survey.diagnosis_stages_qs_num:
            majority_rate = 0
            correctness_rate = 0
        # return redirect(survey.redirect_url or "survey-confirmation", uuid=response.interview_uuid)
        return redirect("survey-confirmation", uuid=response.interview_uuid, majority_rate=majority_rate, correctness_rate=correctness_rate)


    def Diagnostic_Result(self, form, next_url, request, kwargs):

        context = self.result_pre_question(form, next_url, request)
        diagnostic_session_key = "diagnostic_{}_{}".format(request.user, kwargs["survey"].name)
        majority_rate = int(request.session[diagnostic_session_key]["Majority_Rate"])
        correctness_rate = int(request.session[diagnostic_session_key]["Correctness_Rate"])
        is_diagnostic_key = "is_diagnostic_{}_{}".format(request.user, form.survey)
        diagnostic_status = int(cache.get(is_diagnostic_key))
        if diagnostic_status < (form.step+1) * form.survey.diagnosis_stages_qs_num:
            context["diagnostic_result"] = "Sorry,we don't haven enough answers yet."
            context["msg_diagnostic"] = "Zero-Zero"
        else:
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




