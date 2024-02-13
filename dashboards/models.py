from datetime import timedelta
import logging
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.text import slugify
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


############################################################


try:
    from django.conf import settings

    if settings.AUTH_USER_MODEL:
        UserModel = settings.AUTH_USER_MODEL
    else:
        UserModel = User
except (ImportError, AttributeError):
    UserModel = User



try:
    from _collections import OrderedDict
except ImportError:  # pragma: no cover
    from ordereddict import OrderedDict

LOGGER = logging.getLogger(__name__)



############################################################
############################################################

#
#
# def in_duration_day():
#     return now() + timedelta(days=settings.DEFAULT_SURVEY_PUBLISHING_DURATION)
#
#
# def validate_choices(choices):
#     """Verifies that there is at least two choices in choices
#     :param String choices: The string representing the user choices.
#     """
#     values = choices.split(settings.CHOICES_SEPARATOR)
#     empty = 0
#     for value in values:
#         if value.replace(" ", "") == "":
#             empty += 1
#     if len(values) < 2 + empty:
#         msg = "The selected field requires an associated list of choices."
#         msg += " Choices must contain more than one item."
#         raise ValidationError(msg)
#
#
# CHOICES_HELP_TEXT = _(
#     """The choices field is only used if the question type
# if the question type is 'radio', 'select', or
# 'select multiple' provide a comma-separated list of
# options for this question ."""
# )


############################################################
############################################################

class ApplicationUser(AbstractUser):
    gender_choice = {
        ("Other", "Other"),
        ("Male", "Male"),
        ("Female", "Gemale"),
    }
    Gender = models.CharField(
        _("Gender"),
        max_length=10,
        choices=gender_choice,
        default="Other",
        help_text=_("Non-essential items. Please rely on the experimenter's prompts to determine if an answer is required.")
    )
    is_participant = models.BooleanField(
        _("Participant"),
        default=True,
        help_text=_("Newly created users are eligible to participate in the experiment by default.")
    )
    is_experimenter = models.BooleanField(
        _("Experimenter"),
        default=False,
        help_text=_("By default, the added user does not have experimenter privileges. If you need to create an experimenter with administrative rights, select it here.")
    )
    email = models.EmailField(_("E-mail address"),
                              unique=True)
    # USERNAME_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s" % (self.email)
        return full_name.strip()


    def get_short_name(self):
        """Return the short name for the user."""
        full_name = "%s" % (self.email)
        return full_name.strip().split("@",1)[0]


############################################################
############################################################

#
# class Survey(models.Model):
#     ALL_IN_ONE_PAGE = 0
#     BY_QUESTION = 1
#     BY_CATEGORY = 2
#
#     DISPLAY_METHOD_CHOICES = [
#         (BY_QUESTION, _("By question")),
#         (BY_CATEGORY, _("By category")),
#         (ALL_IN_ONE_PAGE, _("All in one page")),
#     ]
#
#     name = models.CharField(_("Name"), max_length=400)
#     description = models.TextField(_("Description"))
#     is_published = models.BooleanField(_("Users can see it and answer it"), default=True)
#     need_logged_user = models.BooleanField(_("Only authenticated users can see it and answer it"))
#     editable_answers = models.BooleanField(_("Users can edit their answers afterwards"), default=True)
#     display_method = models.SmallIntegerField(
#         _("Display method"), choices=DISPLAY_METHOD_CHOICES, default=ALL_IN_ONE_PAGE
#     )
#     template = models.CharField(_("Template"), max_length=255, null=True, blank=True)
#     publish_date = models.DateField(_("Publication date"), blank=True, null=False, default=now)
#     expire_date = models.DateField(_("Expiration date"), blank=True, null=False, default=in_duration_day)
#     redirect_url = models.URLField(_("Redirect URL"), blank=True)
#
#     class Meta:
#         verbose_name = _("survey")
#         verbose_name_plural = _("surveys")
#
#     def __str__(self):
#         return str(self.name)
#
#     @property
#     def safe_name(self):
#         return self.name.replace(" ", "_").encode("utf-8").decode("ISO-8859-1")
#
#     def latest_answer_date(self):
#         """Return the latest answer date.
#
#         Return None is there is no response."""
#         min_ = None
#         for response in self.responses.all():
#             if min_ is None or min_ < response.updated:
#                 min_ = response.updated
#         return min_
#
#     def get_absolute_url(self):
#         return reverse("survey-detail", kwargs={"id": self.pk})
#
#     def non_empty_categories(self):
#         return [x for x in list(self.categories.order_by("order", "id")) if x.questions.count() > 0]
#
#     def is_all_in_one_page(self):
#         return self.display_method == self.ALL_IN_ONE_PAGE
#
#
# ############################################################
# ############################################################
#
# class Response(models.Model):
#
#     """
#     A Response object is a collection of questions and answers with a
#     unique interview uuid.
#     """
#
#     created = models.DateTimeField(_("Creation date"), auto_now_add=True)
#     updated = models.DateTimeField(_("Update date"), auto_now=True)
#     survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_("Survey"), related_name="responses")
#     user = models.ForeignKey(UserModel, on_delete=models.SET_NULL, verbose_name=_("User"), null=True, blank=True)
#     interview_uuid = models.CharField(_("Interview unique identifier"), max_length=36)
#
#     class Meta:
#         verbose_name = _("Set of answers to surveys")
#         verbose_name_plural = _("Sets of answers to surveys")
#
#     def __str__(self):
#         msg = f"Response to {self.survey} by {self.user}"
#         msg += f" on {self.created}"
#         return msg
#
#
# ############################################################
# ############################################################
#
#
# class Category(models.Model):
#     name = models.CharField(_("Name"), max_length=400)
#     survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_("Survey"), related_name="categories")
#     order = models.IntegerField(_("Display order"), blank=True, null=True)
#     description = models.CharField(_("Description"), max_length=2000, blank=True, null=True)
#
#     class Meta:
#         # pylint: disable=too-few-public-methods
#         verbose_name = _("category")
#         verbose_name_plural = _("categories")
#
#     def __str__(self):
#         return self.name
#
#     def slugify(self):
#         return slugify(str(self))
#
#
# ############################################################
# ############################################################
#
#
# class SortAnswer:
#     CARDINAL = "cardinal"
#     ALPHANUMERIC = "alphanumeric"
#
#
# ############################################################
# ############################################################
#
# class Question(models.Model):
#     TEXT = "text"
#     SHORT_TEXT = "short-text"
#     RADIO = "radio"
#     SELECT = "select"
#     SELECT_IMAGE = "select_image"
#     SELECT_MULTIPLE = "select-multiple"
#     INTEGER = "integer"
#     FLOAT = "float"
#     DATE = "date"
#
#     QUESTION_TYPES = (
#         (TEXT, _("text (multiple line)")),
#         (SHORT_TEXT, _("short text (one line)")),
#         (RADIO, _("radio")),
#         (SELECT, _("select")),
#         (SELECT_MULTIPLE, _("Select Multiple")),
#         (SELECT_IMAGE, _("Select Image")),
#         (INTEGER, _("integer")),
#         (FLOAT, _("float")),
#         (DATE, _("date")),
#     )
#
#     text = models.TextField(_("Text"))
#     order = models.IntegerField(_("Order"))
#     required = models.BooleanField(_("Required"))
#     category = models.ForeignKey(
#         Category, on_delete=models.SET_NULL, verbose_name=_("Category"), blank=True, null=True, related_name="questions"
#     )
#     survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_("Survey"), related_name="questions")
#     type = models.CharField(_("Type"), max_length=200, choices=QUESTION_TYPES, default=TEXT)
#     choices = models.TextField(_("Choices"), blank=True, null=True, help_text=CHOICES_HELP_TEXT)
#
#     class Meta:
#         verbose_name = _("question")
#         verbose_name_plural = _("questions")
#         ordering = ("survey", "order")
#
#     def save(self, *args, **kwargs):
#         if self.type in [Question.RADIO, Question.SELECT, Question.SELECT_MULTIPLE]:
#             validate_choices(self.choices)
#         super().save(*args, **kwargs)
#
#     def get_clean_choices(self):
#         """Return split and stripped list of choices with no null values."""
#         if self.choices is None:
#             return []
#         choices_list = []
#         for choice in self.choices.split(settings.CHOICES_SEPARATOR):
#             choice = choice.strip()
#             if choice:
#                 choices_list.append(choice)
#         return choices_list
#
#     @property
#     def answers_as_text(self):
#         """Return answers as a list of text.
#
#         :rtype: List"""
#         answers_as_text = []
#         for answer in self.answers.all():
#             for value in answer.values:
#                 answers_as_text.append(value)
#         return answers_as_text
#
#     @staticmethod
#     def standardize(value, group_by_letter_case=None, group_by_slugify=None):
#         """Standardize a value in order to group by slugify or letter case"""
#         if group_by_slugify:
#             value = slugify(value)
#         if group_by_letter_case:
#             value = value.lower()
#         return value
#
#     @staticmethod
#     def standardize_list(string_list, group_by_letter_case=None, group_by_slugify=None):
#         """Return a list of standardized string from a csv string.."""
#         return [Question.standardize(strng, group_by_letter_case, group_by_slugify) for strng in string_list]
#
#     def answers_cardinality(
#         self,
#         min_cardinality=None,
#         group_together=None,
#         group_by_letter_case=None,
#         group_by_slugify=None,
#         filter=None,
#         other_question=None,
#     ):
#         """Return a dictionary with answers as key and cardinality (int or
#             dict) as value
#
#         :param int min_cardinality: The minimum of answer we need to take it
#             into account.
#         :param dict group_together: A dictionary of value we need to group
#             together. The key (a string) is a placeholder for the list of value
#             it represent (A list of string)
#         :param boolean group_by_letter_case: If true we will group 'Aa' with
#             'aa and 'aA'. You can use group_together as a placeholder if you
#             want everything to be named 'Aa' and not 'aa'.
#         :param boolean group_by_slugify: If true we will group 'Aé b' with
#             'ae-b' and 'aè-B'. You can use group_together as a placeholder if
#             you want everything to be named 'Aé B' and not 'ae-b'.
#         :param list filter: We will exclude every string in this list.
#         :param Question other_question: Instead of returning the number of
#             person that answered the key as value, we will give the cardinality
#             for another answer taking only the user that answered the key into
#             account.
#         :rtype: Dict"""
#         if min_cardinality is None:
#             min_cardinality = 0
#         if group_together is None:
#             group_together = {}
#         if filter is None:
#             filter = []
#             standardized_filter = []
#         else:
#             standardized_filter = Question.standardize_list(filter, group_by_letter_case, group_by_slugify)
#         if other_question is not None:
#             if not isinstance(other_question, Question):
#                 msg = "Question.answer_cardinality expect a 'Question' for "
#                 msg += "the 'other_question' parameter and got"
#                 msg += f" '{other_question}' (a '{other_question.__class__.__name__}')"
#                 raise TypeError(msg)
#         return self.__answers_cardinality(
#             min_cardinality,
#             group_together,
#             group_by_letter_case,
#             group_by_slugify,
#             filter,
#             standardized_filter,
#             other_question,
#         )
#
#     def __answers_cardinality(
#         self,
#         min_cardinality,
#         group_together,
#         group_by_letter_case,
#         group_by_slugify,
#         filter,
#         standardized_filter,
#         other_question,
#     ):
#         """Return an ordered dict but the insertion order is the order of
#         the related manager (ie question.answers).
#
#         If you want something sorted use sorted_answers_cardinality with a set
#         sort_answer parameter."""
#         cardinality = OrderedDict()
#         for answer in self.answers.all():
#             for value in answer.values:
#                 value = self.__get_cardinality_value(value, group_by_letter_case, group_by_slugify, group_together)
#                 if value not in filter and value not in standardized_filter:
#                     if other_question is None:
#                         self._cardinality_plus_n(cardinality, value, 1)
#                     else:
#                         self.__add_user_cardinality(
#                             cardinality,
#                             answer.response.user,
#                             value,
#                             other_question,
#                             group_by_letter_case,
#                             group_by_slugify,
#                             group_together,
#                             filter,
#                             standardized_filter,
#                         )
#         cardinality = self.filter_by_min_cardinality(cardinality, min_cardinality)
#         if other_question is not None:
#             self.__handle_other_question_cardinality(
#                 cardinality,
#                 filter,
#                 group_by_letter_case,
#                 group_by_slugify,
#                 group_together,
#                 other_question,
#                 standardized_filter,
#             )
#         return cardinality
#
#     def filter_by_min_cardinality(self, cardinality, min_cardinality):
#         if min_cardinality != 0:
#             temp = {}
#             for value in cardinality:
#                 if cardinality[value] < min_cardinality:
#                     self._cardinality_plus_n(temp, "Other", cardinality[value])
#                 else:
#                     temp[value] = cardinality[value]
#             cardinality = temp
#         return cardinality
#
#     def __handle_other_question_cardinality(
#         self,
#         cardinality,
#         filter,
#         group_by_letter_case,
#         group_by_slugify,
#         group_together,
#         other_question,
#         standardized_filter,
#     ):
#         """Treating the value for Other question that were not answered in this question"""
#         for answer in other_question.answers.all():
#             for value in answer.values:
#                 value = self.__get_cardinality_value(value, group_by_letter_case, group_by_slugify, group_together)
#                 if value not in filter + standardized_filter:
#                     if answer.response.user is None:
#                         self._cardinality_plus_answer(cardinality, _(settings.USER_DID_NOT_ANSWER), value)
#
#     def sorted_answers_cardinality(
#         self,
#         min_cardinality=None,
#         group_together=None,
#         group_by_letter_case=None,
#         group_by_slugify=None,
#         filter=None,
#         sort_answer=None,
#         other_question=None,
#     ):
#         """Mostly to have reliable tests, but marginally nicer too...
#
#         The ordering is reversed for same cardinality value so we have aa
#         before zz."""
#         # pylint: disable=too-many-locals
#         cardinality = self.answers_cardinality(
#             min_cardinality, group_together, group_by_letter_case, group_by_slugify, filter, other_question
#         )
#         # We handle SortAnswer without enum because using "type" as a variable
#         # name break the enum module and we want to use type in
#         # answer_cardinality for simplicity
#         possibles_values = [SortAnswer.ALPHANUMERIC, SortAnswer.CARDINAL, None]
#         undefined = sort_answer is None
#         user_defined = isinstance(sort_answer, dict)
#         valid = user_defined or sort_answer in possibles_values
#         if not valid:
#             msg = "Unrecognized option '%s' for 'sort_answer': " % sort_answer
#             msg += "use nothing, a dict (answer: rank),"
#             for option in possibles_values:
#                 msg += f" '{option}', or"
#             msg = msg[:-4]
#             msg += ". We used the default cardinal sorting."
#             LOGGER.warning(msg)
#         if undefined or not valid:
#             sort_answer = SortAnswer.CARDINAL
#         sorted_cardinality = None
#         if user_defined:
#             sorted_cardinality = sorted(list(cardinality.items()), key=lambda x: sort_answer.get(x[0], 0))
#         elif sort_answer == SortAnswer.ALPHANUMERIC:
#             sorted_cardinality = sorted(cardinality.items())
#         elif sort_answer == SortAnswer.CARDINAL:
#             if other_question is None:
#                 sorted_cardinality = sorted(list(cardinality.items()), key=lambda x: (-x[1], x[0]))
#             else:
#                 # There is a dict instead of an int
#                 sorted_cardinality = sorted(list(cardinality.items()), key=lambda x: (-sum(x[1].values()), x[0]))
#         return OrderedDict(sorted_cardinality)
#
#     def _cardinality_plus_answer(self, cardinality, value, other_question_value):
#         """The user answered 'value' to our question and
#         'other_question_value' to the other question."""
#         if cardinality.get(value) is None:
#             cardinality[value] = {other_question_value: 1}
#         elif isinstance(cardinality[value], int):
#             # Previous answer did not had an answer to other question
#             cardinality[value] = {_(settings.USER_DID_NOT_ANSWER): cardinality[value], other_question_value: 1}
#         else:
#             if cardinality[value].get(other_question_value) is None:
#                 cardinality[value][other_question_value] = 1
#             else:
#                 cardinality[value][other_question_value] += 1
#
#     def _cardinality_plus_n(self, cardinality, value, n):
#         """We don't know what is the answer to other question but the
#         user answered 'value'."""
#         if cardinality.get(value) is None:
#             cardinality[value] = n
#         else:
#             cardinality[value] += n
#
#     def __get_cardinality_value(self, value, group_by_letter_case, group_by_slugify, group_together):
#         """Return the value we should use for cardinality."""
#         value = Question.standardize(value, group_by_letter_case, group_by_slugify)
#         for key, values in list(group_together.items()):
#             grouped_values = Question.standardize_list(values, group_by_letter_case, group_by_slugify)
#             if value in grouped_values:
#                 value = key
#         return value
#
#     def __add_user_cardinality(
#         self,
#         cardinality,
#         user,
#         value,
#         other_question,
#         group_by_letter_case,
#         group_by_slugify,
#         group_together,
#         filter,
#         standardized_filter,
#     ):
#         values = [_(settings.USER_DID_NOT_ANSWER)]
#         for other_answer in other_question.answers.all():
#             if user is None:
#                 break
#             if other_answer.response.user == user:
#                 # We suppose there is only a response per user
#                 # Why would you want this info if it is
#                 # possible to answer multiple time ?
#                 values = other_answer.values
#                 break
#         for other_value in values:
#             other_value = self.__get_cardinality_value(
#                 other_value, group_by_letter_case, group_by_slugify, group_together
#             )
#             if other_value not in filter + standardized_filter:
#                 self._cardinality_plus_answer(cardinality, value, other_value)
#
#     def get_choices(self):
#         """
#         Parse the choices field and return a tuple formatted appropriately
#         for the 'choices' argument of a form widget.
#         """
#         choices_list = []
#         for choice in self.get_clean_choices():
#             choices_list.append((slugify(choice, allow_unicode=True), choice))
#         choices_tuple = tuple(choices_list)
#         return choices_tuple
#
#     def __str__(self):
#         msg = f"Question '{self.text}' "
#         if self.required:
#             msg += "(*) "
#         msg += f"{self.get_clean_choices()}"
#         return msg
#
#
# ############################################################
# ############################################################
#
#
# class Answer(models.Model):
#     question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name=_("Question"), related_name="answers")
#     response = models.ForeignKey(Response, on_delete=models.CASCADE, verbose_name=_("Response"), related_name="answers")
#     created = models.DateTimeField(_("Creation date"), auto_now_add=True)
#     updated = models.DateTimeField(_("Update date"), auto_now=True)
#     body = models.TextField(_("Content"), blank=True, null=True)
#
#     def __init__(self, *args, **kwargs):
#         try:
#             question = Question.objects.get(pk=kwargs["question_id"])
#         except KeyError:
#             question = kwargs.get("question")
#         body = kwargs.get("body")
#         if question and body:
#             self.check_answer_body(question, body)
#         super().__init__(*args, **kwargs)
#
#     @property
#     def values(self):
#         if self.body is None:
#             return [None]
#         if len(self.body) < 3 or self.body[0:3] != "[u'":
#             return [self.body]
#         # We do not use eval for security reason but it could work with :
#         # eval(self.body)
#         # It would permit to inject code into answer though.
#         values = []
#         raw_values = self.body.split("', u'")
#         nb_values = len(raw_values)
#         for i, value in enumerate(raw_values):
#             if i == 0:
#                 value = value[3:]
#             if i + 1 == nb_values:
#                 value = value[:-2]
#             values.append(value)
#         return values
#
#     def check_answer_body(self, question, body):
#         if question.type in [Question.RADIO, Question.SELECT, Question.SELECT_MULTIPLE]:
#             choices = question.get_clean_choices()
#             self.check_answer_for_select(choices, body)
#         if question.type == Question.INTEGER and body and body != "":
#             try:
#                 body = int(body)
#             except ValueError as e:
#                 msg = "Answer is not an integer"
#                 raise ValidationError(msg) from e
#         if question.type == Question.FLOAT and body and body != "":
#             try:
#                 body = float(body)
#             except ValueError as e:
#                 msg = "Answer is not a number"
#                 raise ValidationError(msg) from e
#
#     def check_answer_for_select(self, choices, body):
#         answers = []
#         if body:
#             if body[0] == "[":
#                 for i, part in enumerate(body.split("'")):
#                     if i % 2 == 1:
#                         answers.append(part)
#             else:
#                 answers = [body]
#         for answer in answers:
#             if answer not in choices:
#                 msg = f"Impossible answer '{body}'"
#                 msg += f" should be in {choices} "
#                 raise ValidationError(msg)
#
#     def __str__(self):
#         return f"{self.__class__.__name__} to '{self.question}' : '{self.body}'"



