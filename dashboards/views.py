import json
import pprint
from datetime import datetime
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.views.generic import View
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.models import Permission
from django.forms import formset_factory
from django.views.generic.edit import FormView
from django.views.generic.edit import UpdateView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.admin.options import get_content_type_for_model
from django.contrib.auth import logout as auth_logout
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.utils.decorators import method_decorator

from django.views.defaults import permission_denied

from dashboards.models import ApplicationUser
from survey.models import Answer
from survey.models.category import Category
from survey.models.survey import Survey
from survey.models.response import Response
from survey.models.question import Question
from survey.models.jumping import Jumping_Question
from survey.models.global_variable import GlobalVariable




from .forms import (ExperimenterCreationForm,
                    ParticipantCreationForm,
                    CreateEveryQuestionForm,
                    CreateQuestionForm,
                    CreateSurveyForm,
                    CreateDefaultRandomForm,
                    GlobalSetupForm,
                    InputExtraNum,
                    CreateControlQuestionForm)

from survey.decorators import survey_available, global_value



class NeverCachemMixin(object):
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(NeverCachemMixin, self)




class HomeIndexView(TemplateView):
    template_name = "home.html"

    @method_decorator(never_cache)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_logged'] = self.request.user.is_authenticated
        return context



class StyleTest(TemplateView):

    template_name = "style.html"

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request=request, **kwargs)
        return self.render_to_response(context)

    def get_context_data(self, request, **kwargs):
        if request.session.get("session_random_list",False):
            del request.session['session_random_list']
            print("Delete session_random_list")
        current_key = "current_key_step_{}".format(request.user)
        step_cache_key = cache.get(current_key)
        if step_cache_key is not None:
        # print("step_cache_key:   ",step_cache_key)
            step_database = cache.get(step_cache_key)
        # print("step_database",step_database)
            if step_database is not None:
                cache.delete(step_cache_key)
                cache.delete(current_key)
                print("Delete step_cache!")
        is_diagnostic_current_key = "current_key_diagnostic_{}".format(request.user)
        is_diagnostic_key = cache.get(is_diagnostic_current_key)
        if is_diagnostic_key is not None:
            diagnostic_status = cache.get(is_diagnostic_key)
            if diagnostic_status is not None:
                cache.delete(is_diagnostic_key)
                cache.delete(is_diagnostic_current_key)
                print("Delete diagnostic_status!")


        context = super().get_context_data(**kwargs)
        context['user_logged'] = self.request.user.is_authenticated
        context['is_staff'] = self.request.user.is_staff
        context['is_superuser'] = self.request.user.is_superuser
        return context


@never_cache
def signup_experimenter(request):
    if request.method == 'POST':
        form = ExperimenterCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if form.cleaned_data.get('extra_field') is not None:
                user.field_1 = form.cleaned_data.get('extra_field')
                user.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')

            user = authenticate(
                username=username,
                password=password
            )

            perm_codename = ["add_category",
                             "change_category",
                             "delete_category",
                             "view_category",
                             "add_survey",
                             "change_survey",
                             "delete_survey",
                             "view_survey",
                             "view_response",
                             "add_question",
                             "change_question",
                             "delete_question",
                             "view_question",
                             "add_answer",
                             "change_answer",
                             "delete_answer",
                             "view_answer",
                             "experimenter",
                             "participant"
                             ]
            for codename in perm_codename:
                user.user_permissions.add(Permission.objects.filter(codename=codename)[0])

            user.is_staff = True
            user.save()
            login(request, user)
            print(user.has_perm('survey.experimenter'))
            print(user.has_perm('survey.participant'))
            return redirect('admin:index')  # Replace 'home' with the URL name of your home page
    else:
        form = ExperimenterCreationForm()
    return render(request, './registration/register_experimenter.html', {'form': form})


@never_cache
def signup_participant(request):
    if request.method == 'POST':
        form = ParticipantCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(
                username=username,
                password=password
            )

            login(request, user)
            ad = Permission.objects.filter(codename='participant')[0]
            user.user_permissions.add(ad)
            return redirect('home_n')
    else:
        form = ParticipantCreationForm()
    return render(request, './registration/register_participant.html', {'form': form})



class My_page(PermissionRequiredMixin,TemplateView):
    template_name = "mypage.html"
    permission_required = ('survey.participant',)

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request=request, **kwargs)
        return self.render_to_response(context)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        response_list = Response.objects.filter(
            user=self.request.user
        )
        # sam-todo:考虑不用每次更新
        response_list_to_desplay = []
        response_list_without_Diagnostic = []
        for response_a in response_list:
            answer_list = Answer.objects.filter(response=response_a).prefetch_related('question')
            ans_count = 0
            for answer in answer_list:
                if answer.question.number_of_responses >= response_a.survey.diagnosis_stages_qs_num:
                    ans_count += response_a.survey.diagnosis_stages_qs_num
                elif answer.question.number_of_responses < response_a.survey.diagnosis_stages_qs_num:
                    ans_count += answer.question.number_of_responses
            if ans_count >= len(answer_list)*int(response_a.number_of_questions):
                response_list_to_desplay.append(response_a)
            else:
                response_list_without_Diagnostic.append(response_a)

        context["answer_list"] = response_list_to_desplay
        context["answer_list_without_Diagnostic"] = response_list_without_Diagnostic
        return context


@permission_required('globalvariable.view_globalvariable',raise_exception=True)
@never_cache
def Global_setup_page(request):
    instance = GlobalVariable.objects.all().first()
    if instance is not None:
        form = GlobalSetupForm(request.POST or None, initial=instance.__dict__)
    else:
        form = GlobalSetupForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            if instance is not None:
                instance.diagnostic_page_indexing = form.cleaned_data["diagnostic_page_indexing"]
                instance.number_of_question = form.cleaned_data["number_of_question"]
                instance.save()

                LogEntry.objects.log_action(
                    user_id=request.user.id,
                    content_type_id=get_content_type_for_model(instance).pk,
                    object_id=instance.id,
                    object_repr=str(instance),
                    action_flag=CHANGE)
            else:
                instance = GlobalVariable.objects.create(
                    diagnostic_page_indexing=form.cleaned_data["diagnostic_page_indexing"],
                    number_of_question=form.cleaned_data["number_of_question"],
                )

            surveys=[]
            for survey in Survey.objects.all():
                survey.diagnostic_page_indexing = instance.diagnostic_page_indexing
                survey.diagnosis_stages_qs_num = instance.diagnostic_page_indexing
                surveys.append(survey)

            Survey.objects.bulk_update(surveys, fields=['diagnostic_page_indexing','diagnosis_stages_qs_num'])


            # if survey_list:
            #     if len(survey_list)==1:
            #         survey = survey_list[0]
            #         survey.download_top_number = instance.download_top_number
            #         survey.diagnostic_page_indexing = instance.diagnostic_page_indexing
            #         survey.diagnosis_stages_qs_num = instance.diagnostic_page_indexing
            #         survey.save()
            #         # question_list = Question.objects.filter(survey=survey)
            #         # if question_list:
            #         #     if len(question_list)==1:
            #         #         question_s = question_list[0]
            #         #
            #         #         question_s.save()
            #         #     elif len(question_list)>1:
            #         #         for question_s in question_list:
            #         #
            #         #             question_s.save()
            #     elif len(survey_list)>1:
            #         for survey_s in survey_list:
            #             survey_s.download_top_number = instance.download_top_number
            #             survey_s.diagnostic_page_indexing = instance.diagnostic_page_indexing
            #             survey_s.diagnosis_stages_qs_num = instance.diagnostic_page_indexing
            #             survey_s.save()
            #             # question_list = Question.objects.filter(survey=survey_s)
            #             # if question_list:
            #             #     if len(question_list) == 1:
            #             #         question_s = question_list[0]
            #             #         question_s.save()
            #             #     elif len(question_list) > 1:
            #             #         for question_s in question_list:
            #             #             question_s.save()
            instance = GlobalVariable.objects.all().first()
            form = GlobalSetupForm(request.POST,initial=instance.__dict__)
            messages.success(request,
                             'GlobalSetupを保存しました。')
            return render(request, 'admin/adminpage/global_setup.html', {'form': form})
    else:
        instance = GlobalVariable.objects.all().first()
        if instance is not None:
            form = GlobalSetupForm(initial=instance.__dict__)
        else:
            form = GlobalSetupForm(request.POST or None)
    return render(request, 'admin/adminpage/global_setup.html', {'form': form})



class Add_survey(View):
    @global_value
    def get(self, request, *args, **kwargs):
        template_name = "../templates/admin/adminpage/addsurvey.html"
        form = CreateSurveyForm(user=request.user, requests=request)
        context = {
            "CreateSurveyForm": form,
        }
        return render(request, template_name, context)

    @global_value
    def post(self, request, *args, **kwargs):
        global_value_dict = kwargs.pop("global_value_dict")
        template_name = "../templates/admin/adminpage/addsurvey.html"
        form = CreateSurveyForm(request.POST, user=request.user, requests=request)
        context = {
            "CreateSurveyForm": form,
        }
        if form.is_valid():
            survey = form.save()
            survey.diagnostic_page_indexing = global_value_dict["diagnostic_page_indexing"]
            survey.download_top_number = global_value_dict["download_top_number"]
            survey.save()

            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=get_content_type_for_model(survey).pk,
                object_id=survey.id,
                object_repr=str(survey),
                action_flag=ADDITION,
                change_message="Add Survey"
            )
            messages.success(self.request, '調査セットを保存しました。')
            if survey is not None:
                return redirect(reverse("add-question-with-id", kwargs={"id": survey.id}))
        return render(request, template_name, context)



class Add_question(View):

    @survey_available
    @global_value
    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        global_value_dict = kwargs.pop("global_value_dict")
        print(global_value_dict)
        template_name = "../templates/admin/adminpage/addquestion.html"
        survey=kwargs.pop("survey")
        if survey.number_of_question < global_value_dict["number_of_question"]:
            color = "red"
        else:
            color = "black"

        context = {
            'survey': survey,
            'color': color,
            'number_of_question': global_value_dict["number_of_question"],
        }
        return render(request, template_name, context)


    @global_value
    @survey_available
    def post(self, request, *args, **kwargs):
        global_value_dict = kwargs.pop("global_value_dict")
        print("post   ",global_value_dict)
        template_name = "../templates/admin/adminpage/addquestion.html"
        survey_id = kwargs.pop("survey_id", None)
        survey = get_object_or_404(
            Survey.objects.prefetch_related("questions", "questions__category"), id=survey_id
        )
        if survey.number_of_question < global_value_dict["number_of_question"]:
            color = "red"
        else:
            color = "black"

        context = {
            'survey': survey,
            'color': color,
            'number_of_question': global_value_dict["number_of_question"],
        }
        return render(request, template_name, context)




class Add_one_random_question_ex(FormView):

    @global_value
    def get(self, request, *args, **kwargs):
        survey_id = kwargs.pop("survey_id", None)
        global_value_dict = kwargs.pop("global_value_dict")
        survey = get_object_or_404(
            Survey.objects.prefetch_related("questions", "questions__category"), id=survey_id
        )
        form = InputExtraNum()
        template_name = "../templates/admin/adminpage/input_extra.html"
        if survey.number_of_question < global_value_dict["number_of_question"]:
            color = "red"
        else:
            color = "black"

        context = {
            'survey': survey,
            'form': form,
            'color': color,
            'number_of_question': global_value_dict["number_of_question"],
        }
        return render(request, template_name, context)

    @global_value
    def post(self, request, *args, **kwargs):
        survey_id = kwargs.pop("survey_id", None)
        form = InputExtraNum(request.POST)
        if form.is_valid():
            data = form.cleaned_data["num"]
            if int(data) in range(1, 11):
                return redirect("add-one-random-question", survey_id=survey_id, extra_num=data)

        template_name = "../templates/admin/adminpage/input_extra.html"
        global_value_dict = kwargs.pop("global_value_dict")
        survey = get_object_or_404(
            Survey.objects.prefetch_related("questions", "questions__category"), id=survey_id
        )
        if survey.number_of_question < global_value_dict["number_of_question"]:
            color = "red"
        else:
            color = "black"
        context = {
            'survey': survey,
            'form': form,
            'color': color,
            'number_of_question': global_value_dict["number_of_question"]
        }
        return render(request, template_name, context)

class Add_one_random_question(FormView):

    @global_value
    def get(self, request, *args, **kwargs):
        survey_id = kwargs.pop("survey_id", None)
        global_value_dict = kwargs.pop("global_value_dict")
        num = kwargs.pop("extra_num")
        num_int = int(num) - 1
        survey = get_object_or_404(
            Survey.objects.prefetch_related("questions", "questions__category"), id=survey_id
        )
        CreateQuestionFormset = formset_factory(CreateQuestionForm, extra=num_int, min_num=1, validate_min=True)
        formset = CreateQuestionFormset(form_kwargs={'user': self.request.user, 'survey': survey, 'requests': self.request})
        template_name = "admin/adminpage/one_random_question.html"
        if survey.number_of_question < global_value_dict["number_of_question"]:
            color = "red"
        else:
            color = "black"

        context = {
            'survey': survey,
            'formset': formset,
            'color': color,
            'number_of_question': global_value_dict["number_of_question"],
            'num':num
        }
        return render(request, template_name, context)

    @global_value
    def post(self, request, *args, **kwargs):
        survey_id = kwargs.pop("survey_id", None)
        global_value_dict = kwargs.pop("global_value_dict")
        num = kwargs.pop("extra_num")
        num_int = int(num) - 1
        survey = get_object_or_404(
            Survey.objects.prefetch_related("questions", "questions__category"), id=survey_id
        )
        CreateQuestionFormset = formset_factory(CreateQuestionForm, extra=num_int, min_num=1, validate_min=True)
        formset = CreateQuestionFormset(request.POST,
            form_kwargs={'user': request.user, 'survey': survey, 'requests': request})
        if survey.number_of_question < global_value_dict["number_of_question"]:
            color = "red"
        else:
            color = "black"

        if formset.is_valid():
            category = Category.objects.create(survey=survey,
                                               block_type="one-random"
                                               )

            for form in formset:
                try:
                    text = form.cleaned_data['text']
                except KeyError:
                    pass
                else:
                    if text != None:
                        question = Question.objects.create(
                            text=text,
                            choices=form.cleaned_data["choice_1_field"]+"|"+form.cleaned_data["choice_2_field"],
                            category=category,
                            survey=survey
                        )
                        question.save()



                        LogEntry.objects.log_action(
                            user_id=request.user.id,
                            content_type_id=get_content_type_for_model(question).pk,
                            object_id=question.id,
                            object_repr=str(question),
                            action_flag=ADDITION,
                            change_message="Add Question"
                        )
            num_question = int(survey.number_of_question)
            num_question += 1
            survey.number_of_question = num_question
            survey.save()
            messages.success(request,
                             '質問を保存しました。調査セット「'+
                             survey.name+
                             '」の質問数：'+str(survey.number_of_question)+
                             '/'+
                              str(global_value_dict["number_of_question"]))
            return redirect(reverse("add-question-with-id", kwargs={"id": survey.id}))

        template_name = "admin/adminpage/one_random_question.html"
        context = {
            'survey': survey,
            'formset': formset,
            'color': color,
            'number_of_question': global_value_dict["number_of_question"],
            'num': num
        }
        return render(request, template_name, context)


class Add_sequence_question_ex(FormView):

    @global_value
    def get(self, request, *args, **kwargs):
        survey_id = kwargs.pop("survey_id", None)
        global_value_dict = kwargs.pop("global_value_dict")
        survey = get_object_or_404(
            Survey.objects.prefetch_related("questions", "questions__category"), id=survey_id
        )
        form = InputExtraNum()
        template_name = "../templates/admin/adminpage/input_extra_sq.html"
        if survey.number_of_question < global_value_dict["number_of_question"]:
            color = "red"
        else:
            color = "black"

        context = {
            'survey': survey,
            'form': form,
            'color': color,
            'number_of_question': global_value_dict["number_of_question"],
        }
        return render(request, template_name, context)

    @global_value
    def post(self, request, *args, **kwargs):
        survey_id = kwargs.pop("survey_id", None)
        form = InputExtraNum(request.POST)
        if form.is_valid():
            data = form.cleaned_data["num"]
            if int(data) in range(1, 11):
                return redirect("add-sequence-question", survey_id=survey_id, extra_num=data)
        template_name = "../templates/admin/adminpage/input_extra_sq.html"
        global_value_dict = kwargs.pop("global_value_dict")
        survey = get_object_or_404(
            Survey.objects.prefetch_related("questions", "questions__category"), id=survey_id
        )
        if survey.number_of_question < global_value_dict["number_of_question"]:
            color = "red"
        else:
            color = "black"
        context = {
            'survey': survey,
            'form': form,
            'color': color,
            'number_of_question': global_value_dict["number_of_question"]
        }
        return render(request, template_name, context)

class Add_sequence_question(FormView):
    @global_value
    def get(self, request, *args, **kwargs):
        survey_id = kwargs.pop("survey_id", None)
        num = kwargs.pop("extra_num")
        num_int = int(num) - 1
        global_value_dict = kwargs.pop("global_value_dict")
        survey = get_object_or_404(
            Survey.objects.prefetch_related("questions", "questions__category"), id=survey_id
        )
        CreateQuestionFormset = formset_factory(CreateQuestionForm, extra=num_int, min_num=1, validate_min=True)
        formset = CreateQuestionFormset(form_kwargs={'user': self.request.user, 'survey': survey, 'requests': self.request})
        if survey.number_of_question < global_value_dict["number_of_question"]:
            color = "red"
        else:
            color = "black"

        template_name = "admin/adminpage/sequence_question.html"
        context = {
            'survey': survey,
            'formset': formset,
            'color': color,
            'number_of_question': global_value_dict["number_of_question"],
            'num':num
        }
        return render(request, template_name, context)

    @global_value
    def post(self, request, *args, **kwargs):
        survey_id = kwargs.pop("survey_id", None)
        num = kwargs.pop("extra_num")
        num_int = int(num) - 1
        global_value_dict = kwargs.pop("global_value_dict")
        survey = get_object_or_404(
            Survey.objects.prefetch_related("questions", "questions__category"), id=survey_id
        )
        CreateQuestionFormset = formset_factory(CreateQuestionForm, extra=num_int, min_num=1, validate_min=True)
        formset = CreateQuestionFormset(request.POST,
            form_kwargs={'user': request.user, 'survey': survey, 'requests': request})

        if formset.is_valid():
            category = Category.objects.create(survey=survey,
                                               block_type="sequence"
                                               )
            for i,form in enumerate(formset):
                try:
                    text = form.cleaned_data['text']
                except KeyError:
                    pass
                else:
                    if text != None:
                        question = Question.objects.create(
                            text=text,
                            choices=form.cleaned_data["choice_1_field"]+"|"+form.cleaned_data["choice_2_field"],
                            category=category,
                            order=i+1,
                            survey=survey
                        )
                        question.save()

                        num_question = int(survey.number_of_question)
                        num_question += 1
                        survey.number_of_question = num_question
                        survey.save()

                        LogEntry.objects.log_action(
                            user_id=request.user.id,
                            content_type_id=get_content_type_for_model(question).pk,
                            object_id=question.id,
                            object_repr=str(question),
                            action_flag=ADDITION,
                            change_message="Add Question")
            messages.success(request,
                             '質問を保存しました。調査セット「'+
                             survey.name+
                             '」の質問数：'+str(survey.number_of_question)+
                             '/'+
                              str(global_value_dict["number_of_question"]))
            return redirect(reverse("add-question-with-id", kwargs={"id": survey.id}))

        template_name = "admin/adminpage/sequence_question.html"
        if survey.number_of_question < global_value_dict["number_of_question"]:
            color = "red"
        else:
            color = "black"
        context = {
            'survey': survey,
            'formset': formset,
            'color': color,
            'number_of_question': global_value_dict["number_of_question"],
            'num': num
        }
        return render(request, template_name, context)



class Add_branch_question(FormView):
    @global_value
    def get(self, request, *args, **kwargs):
        survey_id = kwargs.pop("survey_id", None)
        global_value_dict = kwargs.pop("global_value_dict")
        survey = get_object_or_404(
            Survey.objects.prefetch_related("questions", "questions__category"), id=survey_id
        )
        form = CreateEveryQuestionForm()
        template_name = "admin/adminpage/branch_question.html"
        if survey.number_of_question < global_value_dict["number_of_question"]:
            color = "red"
        else:
            color = "black"
        context = {
            'survey': survey,
            'form': form,
            'color': color,
            'number_of_question': global_value_dict["number_of_question"]
        }
        return render(request, template_name, context)

    @global_value
    def post(self, request, *args, **kwargs):
        survey_id = kwargs.pop("survey_id", None)
        global_value_dict = kwargs.pop("global_value_dict")
        survey = get_object_or_404(
            Survey.objects.prefetch_related("questions", "questions__category"), id=survey_id
        )
        form = CreateEveryQuestionForm(request.POST)

        if form.is_valid():
            jump_question_num = 0
            for key in form.cleaned_data:
                for index in range(2,0,-1):
                    if key == "jumping_"+str(index)+"_question_text":
                        if form.cleaned_data[key] != "":
                            jump_question_num += 1
            category = Category.objects.create(survey=survey,
                                               block_type="branch"
                                               )
            question = Question.objects.create(survey=survey,
                                               category=category,
                                               text=form.cleaned_data["question_text"],
                                               choices=form.cleaned_data["choice_1_field"]+"|"+form.cleaned_data["choice_2_field"],
                                               jump_type="parent-question")
            for i in range(jump_question_num):
                text_label = "jumping_"+str(i+1)+"_question_text"
                choice_1_label = "jumping_"+str(i+1)+"_choice_1_field"
                choice_2_label = "jumping_" + str(i + 1) + "_choice_2_field"

                question_1 = Question.objects.create(survey=survey,
                                                     category=category,
                                                     text=form.cleaned_data[text_label],
                                                     choices=form.cleaned_data[choice_1_label]+"|"+form.cleaned_data[choice_2_label],
                                                     jump_type=str(i+1))
                question_1.save()
                LogEntry.objects.log_action(
                    user_id=request.user.id,
                    content_type_id=get_content_type_for_model(question_1).pk,
                    object_id=question_1.id,
                    object_repr=str(question_1),
                    action_flag = ADDITION,
                    change_message = "Add Question")
            question.save()
            messages.success(request,
                             '質問を保存しました。調査セット「'+
                             survey.name+
                             '」の質問数：'+str(survey.number_of_question)+
                             '/'+
                              str(global_value_dict["number_of_question"]))
            num_question = int(survey.number_of_question)
            num_question += 2
            survey.number_of_question = num_question
            survey.save()
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=get_content_type_for_model(question).pk,
                object_id=question.id,
                object_repr=str(question),
                action_flag=ADDITION,
                change_message="Add Question")
            category.save()
            return redirect(reverse("add-question-with-id", kwargs={"id": survey.id}))
        if survey.number_of_question < global_value_dict["number_of_question"]:
            color = "red"
        else:
            color = "black"
        template_name = "admin/adminpage/branch_question.html"
        context = {
            'survey': survey,
            'form': form,
            'color': color,
            'number_of_question': global_value_dict["number_of_question"]
        }
        return render(request, template_name, context)



class Add_default_random_question(View):
    @global_value
    def get(self, request, *args, **kwargs):
        survey_id = kwargs.pop("survey_id", None)
        global_value_dict = kwargs.pop("global_value_dict")
        survey = get_object_or_404(
            Survey.objects.prefetch_related("questions", "questions__category"),id=survey_id
        )
        form = CreateDefaultRandomForm()
        template_name = "admin/adminpage/question.html"
        if survey.number_of_question < global_value_dict["number_of_question"]:
            color = "red"
        else:
            color = "black"
        context = {
            'survey': survey,
            'form': form,
            'color': color,
            'number_of_question': global_value_dict["number_of_question"]
        }
        return render(request, template_name, context)

    @global_value
    def post(self, request, *args, **kwargs):
        survey_id = kwargs.pop("survey_id", None)
        global_value_dict = kwargs.pop("global_value_dict")
        survey = get_object_or_404(
            Survey.objects.prefetch_related("questions", "questions__category"), id=survey_id
        )
        form = CreateDefaultRandomForm(request.POST)
        template_name = "admin/adminpage/question.html"
        if form.is_valid():
            category_type = "default-random"
            category = Category.objects.create(survey=survey,
                                               block_type=category_type)
            question = form.save()
            question.survey=survey
            question.survey = survey
            question.category=category
            question.choices = form.data.get("choice_1_field") +"|"+ form.data.get("choice_2_field")
            question.save()
            num_question = int(survey.number_of_question)
            num_question += 1
            survey.number_of_question = num_question
            survey.save()
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=get_content_type_for_model(question).pk,
                object_id=question.id,
                object_repr=str(question),
                action_flag=ADDITION,
                change_message="Add Question")
            messages.success(request,
                             '質問を保存しました。調査セット「'+
                             survey.name+
                             '」の質問数：'+str(survey.number_of_question)+
                             '/'+
                              str(global_value_dict["number_of_question"]))
            return redirect(reverse("add-question-with-id", kwargs={"id": survey.id}))
        if survey.number_of_question < global_value_dict["number_of_question"]:
            color = "red"
        else:
            color = "black"
        context = {
            'survey': survey,
            'form': form,
            'color': color,
            'number_of_question': global_value_dict["number_of_question"]
        }

        return render(request, template_name, context)


class Add_control_question_question(View):
    @global_value
    def get(self, request, *args, **kwargs):
        survey_id = kwargs.pop("survey_id", None)
        global_value_dict = kwargs.pop("global_value_dict")
        survey = get_object_or_404(
            Survey.objects.prefetch_related("questions", "questions__category"),id=survey_id
        )
        form = CreateControlQuestionForm()
        template_name = "admin/adminpage/add_control_question.html"
        if survey.number_of_question < global_value_dict["number_of_question"]:
            color = "red"
        else:
            color = "black"
        context = {
            'survey': survey,
            'form': form,
            'color': color,
            'number_of_question': global_value_dict["number_of_question"]
        }
        return render(request, template_name, context)

    @global_value
    def post(self, request, *args, **kwargs):
        survey_id = kwargs.pop("survey_id", None)
        global_value_dict = kwargs.pop("global_value_dict")
        survey = get_object_or_404(
            Survey.objects.prefetch_related("questions", "questions__category"), id=survey_id
        )
        form = CreateControlQuestionForm(request.POST)
        template_name = "admin/adminpage/add_control_question.html"
        if form.is_valid():
            category_type = "control-question"
            category = Category.objects.create(survey=survey,
                                               block_type=category_type)
            question = form.save()
            question.survey=survey
            question.category=category
            question.choices = form.data.get("choice_1_field") +"|"+ form.data.get("choice_2_field")
            question.majority_choices = form.data.get("majority_choices")
            question.save()
            num_question = int(survey.number_of_question)
            num_question += 1
            survey.number_of_question = num_question
            number_of_control_question = int(survey.number_of_control_question)
            number_of_control_question += 1
            survey.number_of_control_question = number_of_control_question
            survey.save()
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=get_content_type_for_model(question).pk,
                object_id=question.id,
                object_repr=str(question),
                action_flag=ADDITION,
                change_message="Add Question")
            messages.success(request,
                             '質問を保存しました。調査セット「'+
                             survey.name+
                             '」の質問数：'+str(survey.number_of_question)+
                             '/'+
                              str(global_value_dict["number_of_question"]))
            return redirect(reverse("add-question-with-id", kwargs={"id": survey.id}))
        if survey.number_of_question < global_value_dict["number_of_question"]:
            color = "red"
        else:
            color = "black"
        context = {
            'survey': survey,
            'form': form,
            'color': color,
            'number_of_question': global_value_dict["number_of_question"]
        }

        return render(request, template_name, context)


class Get_survey_question_num_ajax(View):
    @global_value
    @method_decorator(never_cache)
    def get(self,request ,*args, **kwargs):
        survey_id = request.GET.get("survey_id")
        global_value_dict = kwargs.pop("global_value_dict")
        survey = get_object_or_404(
            Survey.objects.prefetch_related("questions", "questions__category"), id=survey_id
        )
        if survey.number_of_question < global_value_dict["number_of_question"]:
            color = "red"
        else:
            color = "black"
        data = {
            "num_question": survey.number_of_question,
            "color": color
        }
        print(data)
        return HttpResponse(json.dumps(data))



class Surey_Summary(View):
    @global_value
    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        survey_id = kwargs.pop("survey_id", None)
        global_value_dict = kwargs.pop("global_value_dict")
        survey = get_object_or_404(
            Survey.objects, id=survey_id)
        category_list = Category.objects.filter(survey=survey)
        question_list = []
        for category in category_list:
            question_s = Question.objects.filter(survey=survey, category=category)
            question_list.extend(question_s)
        template_name = "../templates/admin/adminpage/surery_summary.html"
        context = {
            'survey': survey,
            "question_list": question_list,
            "category_list": category_list,
            "global_value_dict": global_value_dict,
            "diagnostic_page_indexing": global_value_dict["diagnostic_page_indexing"],
        }

        return render(request, template_name, context)

class Set_survey_public_ajax(View):
    @global_value
    @method_decorator(never_cache)
    def post(self, request, *args, **kwargs):
        survey_id = request.POST.get("survey-id")
        global_value_dict = kwargs.pop("global_value_dict")
        survey = get_object_or_404(
            Survey,id=survey_id
        )

        if request.POST.get("publish_date") != '':
            date_tag_val1 = request.POST.get("publish_date")
            date_tag_val2 = datetime.strptime(date_tag_val1, '%Y-%m-%d')
            date_tag_val = date_tag_val2.date()
            survey.publish_date = date_tag_val
        if request.POST.get("expire_date") != '':
            date_tag_val1 = request.POST.get("expire_date")
            date_tag_val2 = datetime.strptime(date_tag_val1, '%Y-%m-%d')
            date_tag_val = date_tag_val2.date()
            survey.expire_date = date_tag_val
        survey.is_published=True
        survey.save()
        data = {}
        return HttpResponse(json.dumps(data))