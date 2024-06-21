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

from django.contrib.admin.options import get_content_type_for_model
from django.contrib.auth import logout as auth_logout
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import LoginView, LogoutView

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
                    GlobalSetupForm)

from survey.decorators import survey_available, global_value




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
            print(ad)
            user.user_permissions.add(ad)
            print(user.has_perm('survey.participant'))
            return redirect('home_n')  # Replace 'home' with the URL name of your home page
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



def Global_setup_page(request):
    instance = get_object_or_404(GlobalVariable, id=1)
    form = GlobalSetupForm(request.POST or None, initial=instance.__dict__)
    if request.method == 'POST':
        if form.is_valid():
            instance.number_of_responses = form.cleaned_data["number_of_responses"]
            instance.diagnostic_page_indexing = form.cleaned_data["diagnostic_page_indexing"]
            instance.download_top_number = form.cleaned_data["download_top_number"]
            instance.save()

            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=get_content_type_for_model(instance).pk,
                object_id=instance.id,
                object_repr=str(instance),
                action_flag=CHANGE)

            survey_list = Survey.objects.all()
            if survey_list:
                if len(survey_list)==1:
                    survey = survey_list[0]
                    survey.download_top_number = instance.download_top_number
                    survey.diagnostic_page_indexing = instance.diagnostic_page_indexing
                    survey.save()
                    question_list = Question.objects.filter(survey=survey)
                    if question_list:
                        if len(question_list)==1:
                            question_s = question_list[0]
                            question_s.number_of_responses = instance.number_of_responses
                            question_s.save()
                        elif len(question_list)>1:
                            for question_s in question_list:
                                question_s.number_of_responses = instance.number_of_responses
                                question_s.save()
                elif len(survey_list)>1:
                    for survey_s in survey_list:
                        survey_s.download_top_number = instance.download_top_number
                        survey_s.diagnostic_page_indexing = instance.diagnostic_page_indexing
                        survey_s.save()
                        question_list = Question.objects.filter(survey=survey_s)
                        if question_list:
                            if len(question_list) == 1:
                                question_s = question_list[0]
                                question_s.number_of_responses = instance.number_of_responses
                                question_s.save()
                            elif len(question_list) > 1:
                                for question_s in question_list:
                                    question_s.number_of_responses = instance.number_of_responses
                                    question_s.save()
            instance = get_object_or_404(GlobalVariable, id=1)
            form = GlobalSetupForm(request.POST,initial=instance.__dict__)
            return render(request, 'admin/adminpage/global_setup.html', {'form': form})
    else:
        form = GlobalSetupForm(initial=instance.__dict__)
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
    def get(self, request, *args, **kwargs):
        template_name = "../templates/admin/adminpage/addquestion.html"
        survey = kwargs.get("survey")
        context = {
            'survey': survey,
        }
        return render(request, template_name, context)



class Add_one_random_question(FormView):
    def get(self, request, *args, **kwargs):
        survey_id = kwargs.pop("survey_id", None)
        survey = get_object_or_404(
            Survey.objects.prefetch_related("questions", "questions__category"), is_published=True, id=survey_id
        )
        CreateQuestionFormset = formset_factory(CreateQuestionForm, extra=4, min_num=1, validate_min=True)
        formset = CreateQuestionFormset(form_kwargs={'user': self.request.user, 'survey': survey, 'requests': self.request})
        template_name = "admin/adminpage/one_random_question.html"
        context = {
            'survey': survey,
            'formset': formset,
        }
        return render(request, template_name, context)

    @global_value
    def post(self, request, *args, **kwargs):
        survey_id = kwargs.pop("survey_id", None)
        global_value_dict = kwargs.pop("global_value_dict")
        survey = get_object_or_404(
            Survey.objects.prefetch_related("questions", "questions__category"), is_published=True, id=survey_id
        )
        CreateQuestionFormset = formset_factory(CreateQuestionForm, extra=4, min_num=1, validate_min=True)
        formset = CreateQuestionFormset(request.POST,
            form_kwargs={'user': request.user, 'survey': survey, 'requests': request})

        if formset.is_valid():
            category = Category.objects.create(survey=survey,
                                               block_type="one-random"
                                               )

            for form in formset:
                print(form.cleaned_data)
                try:
                    text = form.cleaned_data['text']
                except KeyError:
                    pass
                else:
                    if text != None:
                        question = Question.objects.create(
                            text=text,
                            choices=form.cleaned_data['choices'],
                            category=category,
                            order=form.cleaned_data['order'],
                            survey=survey,
                            number_of_responses=global_value_dict["number_of_responses"]
                        )
                        question.save()

                        LogEntry.objects.log_action(
                            user_id=request.user.id,
                            content_type_id=get_content_type_for_model(question).pk,
                            object_id=question.id,
                            object_repr=str(question),
                            action_flag = ADDITION,
                            change_message = "Add Question"
                        )
            messages.success(self.request, '質問を保存しました。')

            return redirect(reverse("add-question-with-id", kwargs={"id": survey.id}))
        template_name = "admin/adminpage/one_random_question.html"
        context = {
            'survey': survey,
            'formset': formset,
        }
        messages.success(self.request, '質問を保存しました。')
        return render(request, template_name, context)


class Add_sequence_question(FormView):

    def get(self, request, *args, **kwargs):
        survey_id = kwargs.pop("survey_id", None)
        survey = get_object_or_404(
            Survey.objects.prefetch_related("questions", "questions__category"), is_published=True, id=survey_id
        )
        CreateQuestionFormset = formset_factory(CreateQuestionForm, extra=4, min_num=1, validate_min=True)
        formset = CreateQuestionFormset(form_kwargs={'user': self.request.user, 'survey': survey, 'requests': self.request})
        print("Add_sequence_question(順番固定)")
        template_name = "admin/adminpage/sequence_question.html"
        context = {
            'survey': survey,
            'formset': formset,
        }
        return render(request, template_name, context)

    @global_value
    def post(self, request, *args, **kwargs):
        survey_id = kwargs.pop("survey_id", None)
        global_value_dict = kwargs.pop("global_value_dict")
        survey = get_object_or_404(
            Survey.objects.prefetch_related("questions", "questions__category"), is_published=True, id=survey_id
        )
        CreateQuestionFormset = formset_factory(CreateQuestionForm, extra=4, min_num=1, validate_min=True)
        formset = CreateQuestionFormset(self.request.POST,
            form_kwargs={'user': self.request.user, 'survey': survey, 'requests': self.request})
        template_name = "admin/adminpage/sequence_question.html"
        context = {
            'survey': survey,
            'formset': formset,
        }
        if formset.is_valid():
            category = Category.objects.create(survey=survey,
                                               block_type="sequence"
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
                            choices=form.cleaned_data['choices'],
                            category=category,
                            order=form.cleaned_data['order'],
                            survey=survey,
                            number_of_responses=global_value_dict["number_of_responses"]
                        )
                        question.save()
                        LogEntry.objects.log_action(
                            user_id=request.user.id,
                            content_type_id=get_content_type_for_model(question).pk,
                            object_id=question.id,
                            object_repr=str(question),
                            action_flag = ADDITION,
                            change_message = "Add Question")
            messages.success(self.request, '質問を保存しました。')
            return redirect(reverse("add-question-with-id", kwargs={"id": survey.id}))
        return render(request, template_name, context)



class Add_branch_question(FormView):

    def get(self, request, *args, **kwargs):
        survey_id = kwargs.pop("survey_id", None)
        survey = get_object_or_404(
            Survey.objects.prefetch_related("questions", "questions__category"), is_published=True, id=survey_id
        )
        form = CreateEveryQuestionForm()
        template_name = "admin/adminpage/branch_question.html"
        context = {
            'survey': survey,
            'form': form,
        }
        return render(request, template_name, context)

    @global_value
    def post(self, request, *args, **kwargs):
        survey_id = kwargs.pop("survey_id", None)
        global_value_dict = kwargs.pop("global_value_dict")
        survey = get_object_or_404(
            Survey.objects.prefetch_related("questions", "questions__category"), is_published=True, id=survey_id
        )
        form = CreateEveryQuestionForm(request.POST)

        if form.is_valid():
            jump_question_num = 0
            for key in form.cleaned_data:
                for index in range(4,0,-1):
                    if key == "jumping_"+str(index)+"_choices_order":
                        if form.cleaned_data[key] != "":
                            jump_question_num += 1
            category = Category.objects.create(survey=survey,
                                               block_type="branch"
                                               )
            question = Question.objects.create(survey=survey,
                                               category=category,
                                               text=form.cleaned_data["question_text"],
                                               choices=form.cleaned_data["question_choices"],
                                               jump_type="parent-question",
                                               number_of_responses=global_value_dict["number_of_responses"])
            for i in range(jump_question_num):
                text_label = "jumping_"+str(i+1)+"_question_text"
                choice_label = "jumping_"+str(i+1)+"_question_choices"
                question_1 = Question.objects.create(survey=survey,
                                                     category=category,
                                                     text=form.cleaned_data[text_label],
                                                     choices=form.cleaned_data[choice_label],
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
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=get_content_type_for_model(question).pk,
                object_id=question.id,
                object_repr=str(question),
                action_flag=ADDITION,
                change_message="Add Question")
            category.save()
            return redirect(reverse("add-question-with-id", kwargs={"id": survey.id}))
        template_name = "admin/adminpage/branch_question.html"
        context = {
            'survey': survey,
            'form': form,
        }
        messages.success(self.request, '質問を保存しました。')
        return render(request, template_name, context)


class Add_default_random_question(View):
    def get(self, request, *args, **kwargs):
        survey_id = kwargs.pop("survey_id", None)
        survey = get_object_or_404(
            Survey.objects.prefetch_related("questions", "questions__category"), is_published=True, id=survey_id
        )
        form = CreateDefaultRandomForm()
        template_name = "admin/adminpage/question.html"
        context = {
            'survey': survey,
            'form': form,
        }
        return render(request, template_name, context)

    @global_value
    def post(self, request, *args, **kwargs):
        survey_id = kwargs.pop("survey_id", None)
        global_value_dict = kwargs.pop("global_value_dict")
        survey = get_object_or_404(
            Survey.objects.prefetch_related("questions", "questions__category"), is_published=True, id=survey_id
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
            question.number_of_responses=global_value_dict["number_of_responses"]
            question.save()
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=get_content_type_for_model(question).pk,
                object_id=question.id,
                object_repr=str(question),
                action_flag=ADDITION,
                change_message="Add Question")
            return redirect(reverse("add-question-with-id", kwargs={"id": survey.id}))

        context = {
            'survey': survey,
            'form': form,
        }
        messages.success(self.request, '質問を保存しました。')
        return render(request, template_name, context)






