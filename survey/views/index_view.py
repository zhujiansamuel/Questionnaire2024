import time
from datetime import date
import csv
from django.urls import reverse
from django.contrib.auth.mixins import PermissionRequiredMixin

from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from survey.models import Survey, Response, Answer, Question, Category
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from ..forms import UploadFileForm
import sys
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
import django.dispatch
from django.dispatch import receiver

init_cache = django.dispatch.Signal()

# class IndexView(TemplateView):
class ConsentsView(PermissionRequiredMixin,TemplateView):
    template_name = "survey/consents_page.html"
    permission_required = ('survey.participant',)
    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data( **kwargs)
        return self.render_to_response(context)


class IndexView(PermissionRequiredMixin,TemplateView):
    template_name = "survey/list.html"
    permission_required = ('survey.participant',)

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request, **kwargs)
        return self.render_to_response(context)

    def get_context_data(self,request,  **kwargs):
        context = super().get_context_data(**kwargs)
        surveys = Survey.objects.filter(
            is_published=True, expire_date__gte=date.today(), publish_date__lte=date.today()
        )
        survey_unanswered = []
        for survey in surveys:
            responses = Response.objects.filter(survey=survey, user=request.user).exists()
            if not responses:
                survey_unanswered.append(survey)
            session_key = "survey_{}".format(survey.id)
            diagnostic_session_key = "diagnostic_{}_{}".format(request.user, survey.name)
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

            current_key = "current_key_step_{}".format(request.user)
            step_cache_key = cache.get(current_key)
            if step_cache_key is not None:
                step_database = cache.get(step_cache_key)
                if step_database is not None:
                    cache.delete(step_cache_key)
                    cache.delete(current_key)
            is_diagnostic_current_key = "current_key_diagnostic_{}".format(request.user)
            is_diagnostic_key = cache.get(is_diagnostic_current_key)
            if is_diagnostic_key is not None:
                diagnostic_status = cache.get(is_diagnostic_key)
                if diagnostic_status is not None:
                    cache.delete(is_diagnostic_key)
                    cache.delete(is_diagnostic_current_key)
                    # print("Delete diagnostic_status!------1")

        if request.session.get("session_random_list",False):
            del request.session['session_random_list']
            print("Delete session_random_list")


        if not self.request.user.has_perm('survey.participant'):
            print("permission_denied")
        if not self.request.user.is_authenticated:
            surveys = surveys.filter(need_logged_user=True)

        context["surveys"] = survey_unanswered
        context["user_logged"] = self.request.user.is_authenticated,
        context["is_experimenter"] = self.request.user.has_perm('survey.experimenter')

        return context


class ExperimenterLoginView(TemplateView):
    template_name = "to_register_experimenter.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def download_csv(request, survey_id):
    survey = Survey.objects.filter(pk=survey_id).first()
    survey_name = str(survey.name)
    time_str = str(time.time())
    filename = survey_name + time_str + str(request.user) + ".csv"
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename=' + filename + "'"},
    )
    writer = csv.writer(response)
    writer.writerow(['All id',
                     'User',
                     'User Email',
                     'Survey',
                     'Response ID',
                     'Question ID',
                     'Question',
                     'Question Answer',
                     'Mate Subsidiary Question',
                     'Majority Choices'
                     ])
    survey_response = Response.objects.filter(survey=survey)
    all_order = 1
    if survey_response.count()>1:
        for s_r in survey_response:
            answer_s = Answer.objects.filter(response=s_r).prefetch_related("question")
            for a_s in answer_s:
                writer.writerow([str(all_order),
                                 str(s_r.user),
                                 ' ',
                                 str(s_r.survey.name),
                                 str(s_r.pk),
                                 str(a_s.question.pk),
                                 str(a_s.question.text),
                                 str(a_s.body),
                                 str(a_s.question.majority_minority),
                                 str(a_s.question.majority_choices)
                                 ])
                all_order += 1

    return response

def upload_survey(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            sys.stderr.write("*** file_upload *** aaa ***\n")
            handle_uploaded_file(request.FILES['file'], request.user)
            return redirect('admin:index')
    else:
        form = UploadFileForm()
    return render(request, 'upload_csv.html', {'form': form})


def handle_uploaded_file(file_obj,user):
    file_path = 'media/upload/' + file_obj.name
    with open(file_path, 'wb+') as destination:
        for chunk in file_obj.chunks():
            destination.write(chunk)

    file_title = str(file_obj.name).split('_')
    survey = Survey.objects.get_or_create(name=file_title[0])[0]
    if file_title[1] == 'Survey':
        with open(file_path, 'r') as destination:
            reader = csv.DictReader(destination)
            for row in reader:
                survey.description = row['Description']
                survey.founder = user
                survey.save()

    elif file_title[1] == 'Category':
        with open(file_path, 'r') as destination:
            reader = csv.DictReader(destination)
            for row in reader:
                Category.objects.create(
                    name=row['Name'],
                    survey=survey,
                    description=row['Description'],
                    display_num=row['Display Number'],
                    hiding_question_order=row['Hiding Question Order'],
                    block_type=row['Block Type']
                )

    elif file_title[1] == 'Question':
        with open(file_path, 'r') as destination:
            reader = csv.DictReader(destination)
            for row in reader:
                try:
                    category = Category.objects.get(name=row['Category'])
                except Category.DoesNotExist:
                    category = Category.objects.create(
                        name=row['Category'],
                        survey=survey
                )
                try:
                    question = Question.objects.get(markings=row['Markings'])
                    question.text=row['Text']
                    question.order = row['Order']
                    question.category = category
                    question.choices = row['Choice']
                    question.hiding_question_category_order = row['Hiding Question Order']
                    question.save()
                except Question.DoesNotExist:
                    Question.objects.create(
                        markings=row['Markings'],
                        text=row['Text'],
                        order=row['Order'],
                        category=category,
                        survey=survey,
                        choices=row['Choice'],
                        hiding_question_category_order=row['Hiding Question Order']
                    )


#
# ------------------------------------------------------------------
def success(request):
    str_out = "Success!<p />"
    return HttpResponse(str_out)


def response_detail(request, survey_id):
    pass


@receiver(init_cache, sender=IndexView)
def my_callback(sender, **kwargs):
    print("收到信号")