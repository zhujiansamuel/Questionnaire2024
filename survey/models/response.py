from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
# from survey.utility.recalculated_results import calculate_results
from survey.utility.diagnostic_result import Diagnostic_Result

from .survey import Survey

try:
    from django.conf import settings

    if settings.AUTH_USER_MODEL:
        UserModel = settings.AUTH_USER_MODEL
    else:
        UserModel = User
except (ImportError, AttributeError):
    UserModel = User


class Response(models.Model):
    INITIAL_STATE = "Initial state"
    IN_PROGRESS = "In progress"
    COMPLETED = "Completed"

    COMPLETION_STATUS_CHOICE = (
        (INITIAL_STATE, _("Initial state")),
        (IN_PROGRESS, _("In progress")),
        (COMPLETED, _("Completed")),
    )
    """
    A Response object is a collection of questions and answers with a
    unique interview uuid.
    """

    created = models.DateTimeField(_("Creation date"), auto_now_add=True)
    updated = models.DateTimeField(_("Update date"), auto_now=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_("Survey"), related_name="responses")
    user = models.ForeignKey(UserModel, on_delete=models.SET_NULL, verbose_name=_("User"), null=True, blank=True)
    Majority_Rate = models.CharField(_("Majority Rate"), default="0", max_length=20)
    Correctness_Rate = models.CharField(_("Correctness Rate"), default="0", max_length=20)
    interview_uuid = models.CharField(_("ID"), max_length=36)
    repeat_order = models.IntegerField(_("Order of repeated"), default=0)
    completion_status = models.CharField(_("completion_status"), max_length=50, choices=COMPLETION_STATUS_CHOICE, default="Initial state")

    number_of_questions = models.IntegerField(_("Number of questions"), default=0)
    number_of_control_question = models.IntegerField(_("コントロール質問の数"), default=0)

    Majority_Rate_num = models.CharField(_("Majority Rate(Number)"), default=0, max_length=20)
    Correctness_Rate_num = models.CharField(_("Correctness Rate(Number)"), default=0, max_length=20)
    DIAGNOSTIC_RESULT = models.CharField(_("DIAGNOSTIC"), default="Zero", max_length=20)
    survey_founder = models.ForeignKey(UserModel, on_delete=models.SET_NULL, verbose_name=_("survey_founder"), null=True, blank=True,related_name="survey_responses")


    class Meta:
        verbose_name = _("Set of answers")
        verbose_name_plural = _("Sets of answers")

    def __str__(self):
        msg = f"Response to {self.survey}"
        msg += f" on {self.created.date()}."
        return msg

    def display_with_diagnostic(self):
        msg = f"Response to {self.survey}"
        msg += f" on {self.created.date()}."
        msg += f" Diagnostic result is {self.DIAGNOSTIC_RESULT}."

        return msg

    def get_details(self):
        pass

