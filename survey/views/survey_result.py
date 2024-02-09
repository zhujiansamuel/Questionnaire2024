from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect

from survey.exporter.csv.survey2csv import Survey2Csv
from survey.models import Survey


def serve_unprotected_result_csv(survey):
    """Return the csv corresponding to a survey."""
    survey_to_csv = Survey2Csv(survey)
    if survey_to_csv.need_update():
        survey_to_csv.generate_file()
    with open(survey_to_csv.filename) as csv_file:
        response = HttpResponse(csv_file.read(), content_type="text/csv")
    content_disposition = f'attachment; filename="{survey.name}.csv"'
    response["Content-Disposition"] = content_disposition
    return response


@login_required
def serve_protected_result(request, survey):
    """Return the csv only if the user is logged."""
    return serve_unprotected_result_csv(survey)


def serve_result_csv(request, primary_key):
    """... only if the survey does not require login or the user is logged.

    :param int primary_key: The primary key of the survey."""
    survey = get_object_or_404(Survey, pk=primary_key)
    if not survey.is_published:
        messages.error(request, "This survey has not been published")
        return redirect(f"{settings.LOGIN_URL}?next={request.path}")
    if survey.need_logged_user:
        return serve_protected_result(request, survey)
    return serve_unprotected_result_csv(survey)
