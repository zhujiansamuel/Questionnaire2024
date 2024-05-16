from datetime import timedelta
from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

try:
    from django.conf import settings

    if settings.AUTH_USER_MODEL:
        UserModel = settings.AUTH_USER_MODEL
    else:
        UserModel = User
except (ImportError, AttributeError):
    UserModel = User



NAME_HELP_TEXT = _("""

""")

DESCRIPTION_HELP_TEXT = _("""

""")

IS_PUBLISHED_HELP_TEXT = _("""

""")

PUBLISH_DATE_HELP_TEXT = _("""

""")

EXPIRE_DATE_HELP_TEXT = _("""

""")

DIAGNOSIS_STAGES_QS_NUM_HELP_TEXT = _("""
Displays temporary diagnostic information after how many questions have been answered.
""")

DIAGNOSTIC_PAGE_INDEXING = _("""
The diagnosis is displayed after collecting as many responses as possible.
""")

DOWNLOAD_TOP_NUMBER = _("""
Decide how many downloads the most points for the answer.If set to 0, then download all responses
""")

FOUNDER = _("""
Creator of the questionnaire. Creators can only view and edit their own questionnaires.
""")

def in_duration_day():
    return now() + timedelta(days=settings.DEFAULT_SURVEY_PUBLISHING_DURATION)


class Survey(models.Model):
    ALL_IN_ONE_PAGE = 0
    BY_QUESTION = 1
    BY_CATEGORY = 2

    DISPLAY_METHOD_CHOICES = [
        (BY_QUESTION, _("By question")),
        (BY_CATEGORY, _("By category")),
        (ALL_IN_ONE_PAGE, _("All in one page")),
    ]

    name = models.CharField(_("Name"), max_length=400, help_text=NAME_HELP_TEXT)
    description = models.TextField(_("Description"), help_text=DESCRIPTION_HELP_TEXT)
    is_published = models.BooleanField(_("answer-able"), default=True, help_text=IS_PUBLISHED_HELP_TEXT)
    founder = models.ForeignKey(UserModel, on_delete=models.SET_NULL, verbose_name=_("Founder"), null=True, blank=True, help_text=FOUNDER)
    need_logged_user = models.BooleanField(_("Only authenticated users can see it and answer it"), default=True)
    editable_answers = models.BooleanField(_("Users can edit their answers afterwards"), default=True)
    display_method = models.SmallIntegerField(
        _("Display method"), choices=DISPLAY_METHOD_CHOICES, default=BY_QUESTION
    )

    template = models.CharField(_("Template"), max_length=255, null=True, blank=True)
    publish_date = models.DateField(_("Publication date"), blank=True, null=False, default=now, help_text=PUBLISH_DATE_HELP_TEXT)
    expire_date = models.DateField(_("Expiration date"), blank=True, null=False, default=in_duration_day, help_text=EXPIRE_DATE_HELP_TEXT)
    redirect_url = models.URLField(_("Redirect URL"), blank=True)
    diagnosis_stages_qs_num = models.IntegerField(_("Diagnosis of stages"), default=10, help_text=DIAGNOSIS_STAGES_QS_NUM_HELP_TEXT)

    diagnostic_page_indexing = models.IntegerField(_("Diagnostic page indexing"), default=10, help_text=DIAGNOSTIC_PAGE_INDEXING)
    download_top_number = models.IntegerField(_("Download the top results"), default=0, help_text=DOWNLOAD_TOP_NUMBER)

    class Meta:
        verbose_name = _("survey")
        verbose_name_plural = _("surveys")
        permissions = (
            ("participant","Questionnaires can be filled out"),
            ("experimenter","Possibility to edit the survey"),
        )

    def __str__(self):
        return str(self.name)


    @property
    def safe_name(self):
        return self.name.replace(" ", "_").encode("utf-8").decode("ISO-8859-1")

    def latest_answer_date(self):
        """Return the latest answer date.

        Return None is there is no response."""
        min_ = None
        for response in self.responses.all():
            if min_ is None or min_ < response.updated:
                min_ = response.updated
        return min_

    def get_absolute_url(self):
        return reverse("survey-detail", kwargs={"id": self.pk})

    def non_empty_categories(self):
        # 这里显示由order与id控制分类显示的顺序
        return [x for x in list(self.categories.order_by("order", "id")) if x.questions.count() > 0]

    def random_categories(self):
        return [x for x in list(self.categories.order_by("id")) if x.questions.count() > 0 and x.name != "hiding_question"]

    def is_all_in_one_page(self):
        return self.display_method == self.ALL_IN_ONE_PAGE

    def create_hiding_questions(self):
        self.categories.create(
            name="hiding_question",
            order=0,
            description="Every newly created survey file has this default category.",
            random_order=0,
            display_num=100
        )

