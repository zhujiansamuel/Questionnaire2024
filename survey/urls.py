try:
    from django.conf.urls import url
except ImportError:
    # Django 4.0 replaced url by something else
    # See https://stackoverflow.com/a/70319607/2519059
    from django.urls import re_path as url

from survey.views import ConfirmView, IndexView, SurveyCompleted, SurveyDetail
from survey.views.survey_result import serve_result_csv
from survey.views.index_view import download_csv



urlpatterns = [
    url(r"^$", IndexView.as_view(), name="survey-list"),
    url(r"^(?P<id>\d+)/", SurveyDetail.as_view(), name="survey-detail"),
    url(r"^csv/(?P<primary_key>\d+)/", serve_result_csv, name="survey-result"),
    url(r"^(?P<id>\d+)/completed/", SurveyCompleted.as_view(), name="survey-completed"),
    url(r"^(?P<id>\d+)-(?P<step>\d+)/", SurveyDetail.as_view(), name="survey-detail-step"),
    url(r"^confirm/(?P<uuid>\w+)/(?P<majority_rate>\w+)-(?P<correctness_rate>\w+)", ConfirmView.as_view(), name="survey-confirmation"),
    url(r"^download/(?P<survey_id>\d+)", download_csv, name="download-csv"),
    # url(r"^response/(?P<id>\d+)/")
]
