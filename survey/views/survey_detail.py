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

    @survey_available
    def get(self, request, *args, **kwargs):
        survey = kwargs.get("survey")
        step = kwargs.get("step", 0)
        is_diagnostic_key = "is_diagnostic_{}_{}".format(request.user, survey)
        is_diagnostic_current_key = "current_key_diagnostic_{}".format(request.user)
        cache.set(is_diagnostic_current_key, is_diagnostic_key)
        diagnostic_status = cache.get(is_diagnostic_key)
        if not diagnostic_status:
            cache.set(is_diagnostic_key, 0)

        step_cache_key = "step_{}_{}".format(request.user,survey)
        current_key = "current_key_step_{}".format(request.user)
        cache.set(current_key, step_cache_key)
        step_database = cache.get(step_cache_key)

        if step_database is not None:
            if int(step_database) != int(step):
                messages.warning(request, "It appears that your experimental process has been interrupted. We will restart the experiment.")
                return redirect("home_n")
        elif step_database is None and int(step)!=0:
            messages.warning(request,
                             "It appears that your experimental process has been interrupted. We will restart the experiment.")
            return redirect("home_n")


        control_question_key = "control_question_{}_{}".format(request.user,survey.name)
        current_control_question_key = "current_key_control_question_{}".format(request.user)
        cache.set(current_control_question_key, control_question_key)
        control_question_ = cache.get(control_question_key)
        if not control_question_:
            cache.set(control_question_key, 0)


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
        # 配置缓存，特别是第一次生成表格
        if diagnostic_session_key not in request.session:
            request.session[diagnostic_session_key] = {}
            request.session.modified = True
            request.session[diagnostic_session_key]["Majority_Rate"] = "0"
            request.session.modified = True
            request.session[diagnostic_session_key]["Correctness_Rate"] = "0"
            request.session.modified = True
            request.session[diagnostic_session_key]["Valid_Questions"] = "0"
            request.session.modified = True

        majority_rate = int(request.session[diagnostic_session_key]["Majority_Rate"])
        correctness_rate = int(request.session[diagnostic_session_key]["Correctness_Rate"])
        valid_questions = int(request.session[diagnostic_session_key]["Valid_Questions"])

        # 已答题计数器（不含控制题），用于每N题诊断触发
        is_diagnostic_key = "is_diagnostic_{}_{}".format(request.user, survey)
        answered_count = int(cache.get(is_diagnostic_key) or 0)

        session_key = "survey_{}".format(kwargs["id"])
        if session_key not in request.session:
            request.session[session_key] = {}

        # 遍历本步提交的数据，提取主题和附属题，正确关联 question 对象
        # 先收集本步所有主题的 question 对象和选择值
        step_questions = {}  # {q_id: (question, choice)}
        for field_name, field_value in list(form.cleaned_data.items()):
            if field_name.startswith("question_") and not field_name.startswith("question_subsidiary_"):
                q_id = int(field_name.split("_")[1])
                question = Question.objects.get(pk=q_id)
                step_questions[q_id] = (question, field_value)

        # 保存所有 cleaned_data 到 session
        for key, value in list(form.cleaned_data.items()):
            request.session[session_key][key] = value
            request.session.modified = True

        # 计算多数率、正确率，并更新已答题计数
        for q_id, (question, choice) in step_questions.items():
            # 处理分支块的缓存标记
            if question.category.block_type == "branch":
                branch_mark_key = "branch_mark_{}_{}_{}".format(request.user, survey, question.category)
                branch_mark = cache.get(branch_mark_key)
                if branch_mark is None:
                    cache.set(branch_mark_key, question.get_choice_index(choice))

            # 跳过控制题，不计入诊断
            if question.category.block_type == "control-question":
                continue

            # 累加已答题数（非控制题）
            answered_count += 1
            cache.set(is_diagnostic_key, answered_count)

            # 阈值检查：该题回答数未达到 diagnostic_page_indexing 时，不计入诊断指标
            if question.number_of_responses < survey.diagnostic_page_indexing:
                continue

            # 该题达到阈值，计入有效题数
            valid_questions += 1
            request.session[diagnostic_session_key]["Valid_Questions"] = str(valid_questions)
            request.session.modified = True

            # 根据附属题类型计算多数率和正确率
            if question.subsidiary_type == "majority_minority":
                subsidiary_key = "question_subsidiary_{}".format(q_id)
                subsidiary_value = form.cleaned_data.get(subsidiary_key)
                if subsidiary_value == "majority":
                    majority_rate += 1
                    request.session[diagnostic_session_key]["Majority_Rate"] = str(majority_rate)
                    request.session.modified = True
                    if question.majority_choices == choice:
                        correctness_rate += 1
                        request.session[diagnostic_session_key]["Correctness_Rate"] = str(correctness_rate)
                        request.session.modified = True
                elif subsidiary_value == "minority":
                    if question.majority_choices != "Null" and question.majority_choices != choice:
                        correctness_rate += 1
                        request.session[diagnostic_session_key]["Correctness_Rate"] = str(correctness_rate)
                        request.session.modified = True
            elif question.subsidiary_type == "certainty_degree":
                pass

        next_url = form.next_step_url()
        response = None
        session_random_list = request.session.get("session_random_list", False)
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
            # 判断是否需要触发每N题阶段性诊断
            diagnosis_n = survey.diagnosis_stages_qs_num
            if diagnosis_n > 0 and answered_count > 0 and answered_count % diagnosis_n == 0:
                context = self.Diagnostic_Result(form, next_url, request, kwargs, valid_questions)
            else:
                context = self.result_pre_question(form, next_url, request)
            template_name = "survey/result_pre_question.html"
            return render(request, template_name, context)

        if response is None:
            return redirect(reverse("survey-list"))
        next_ = request.session.get("next", None)
        if next_ is not None:
            if "next" in request.session:
                del request.session["next"]
            return redirect(next_)

        # 最终确认页：传入有效题数用于诊断计算
        return redirect(
            "survey-confirmation",
            uuid=response.interview_uuid,
            majority_rate=majority_rate,
            correctness_rate=correctness_rate,
            valid_questions=valid_questions,
        )


    def Diagnostic_Result(self, form, next_url, request, kwargs, valid_questions):
        """每N题触发的阶段性诊断结果展示"""
        context = self.result_pre_question(form, next_url, request)
        diagnostic_session_key = "diagnostic_{}_{}".format(request.user, kwargs["survey"].name)
        majority_rate = int(request.session[diagnostic_session_key]["Majority_Rate"])
        correctness_rate = int(request.session[diagnostic_session_key]["Correctness_Rate"])

        if valid_questions == 0:
            context["diagnostic_result"] = "まだ十分な回答が集まっていないため、診断を表示できません。"
            context["msg_diagnostic"] = "Zero-Zero"
        else:
            msg, diagnostic_result_msg, _, _ = Diagnostic_Analyze(majority_rate, correctness_rate, valid_questions)
            context["diagnostic_result"] = diagnostic_result_msg
            context["msg_diagnostic"] = msg
        return context


    def result_pre_question(self, form, next_url, request):
        not_enough = True
        msg = ""

        # 先收集每道主题的 choice，以 q_id 为 key
        question_choices = {}
        for field_name, field_value in list(form.cleaned_data.items()):
            if field_name.startswith("question_") and not field_name.startswith("question_subsidiary_"):
                q_id = int(field_name.split("_")[1])
                question_choices[q_id] = field_value

        # 再处理附属题，正确关联对应主题的 question 和 choice
        for field_name, field_value in list(form.cleaned_data.items()):
            if not field_name.startswith("question_subsidiary_"):
                continue

            subsidiary_value = field_value
            pk = int(field_name.split("_")[2])
            question = Question.objects.get(pk=pk)
            choice = question_choices.get(pk, "")

            if question.category.block_type != "control-question":
                if question.number_of_responses < question.survey.diagnostic_page_indexing:
                    not_enough = True
                    msg = "あなたの回答の正解・不正解はまだ十分に回答が集まっていないため、後ほどまたログインして確かめてください."
                else:
                    not_enough = False
                    if question.subsidiary_type == "majority_minority":
                        if question.majority_choices == choice:
                            if subsidiary_value == "majority":
                                msg = "正解、あなたの回答は多数派"
                            else:
                                msg = "不正解、あなたの回答は多数派"
                        else:
                            if subsidiary_value == "minority":
                                msg = "正解、あなたの回答は少数派"
                            else:
                                msg = "不正解、あなたの回答は少数派"
            else:
                # 控制题：也显示正解/不正解反馈，但额外跟踪错误次数
                if question.subsidiary_type == "majority_minority":
                    is_correct = False
                    if question.majority_choices == choice:
                        if subsidiary_value == "majority":
                            msg = "正解、あなたの回答は多数派"
                            is_correct = True
                        else:
                            msg = "不正解、あなたの回答は多数派"
                    else:
                        if subsidiary_value == "minority":
                            msg = "正解、あなたの回答は少数派"
                            is_correct = True
                        else:
                            msg = "不正解、あなたの回答は少数派"

                    if not is_correct:
                        control_question_key = "control_question_{}_{}".format(request.user, question.survey.name)
                        control_question_ = int(cache.get(control_question_key) or 0) + 1
                        cache.set(control_question_key, control_question_)

        context = {
            "next_url": next_url,
            "not_enough": not_enough,
            "msg": msg,
        }

        return context




