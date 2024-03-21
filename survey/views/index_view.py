import time
from datetime import date
import csv
from django.urls import reverse
from django.contrib.auth.mixins import PermissionRequiredMixin

from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from survey.models import Survey, Response, Answer, Question


class IndexView(PermissionRequiredMixin,TemplateView):

    template_name = "survey/list.html"
    permission_required = ('survey.participant', 'survey.experimenter')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        surveys = Survey.objects.filter(
            is_published=True, expire_date__gte=date.today(), publish_date__lte=date.today()
        )
        if not self.request.user.is_authenticated:
            surveys = surveys.filter(need_logged_user=True)
        context["surveys"] = surveys
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
