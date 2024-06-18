import logging
import random
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .category import Category
from .survey import Survey

try:  # pragma: no cover
    from _collections import OrderedDict
except ImportError:  # pragma: no cover
    from ordereddict import OrderedDict

from django_ckeditor_5.fields import CKEditor5Field

# from ckeditor_uploader.fields import RichTextUploadingField

LOGGER = logging.getLogger(__name__)


CHOICES_HELP_TEXT = _(
    """
When entering options, use "|" to separate different options. For example, a|b|c.

"""
)

TEXT_HELP_TEXT = _("""

""")

ORDER_HELP_TEXT = _("""
If the type of the Category to which the question belongs is SEQUENCE, 
this value determines the order in which the questions are displayed in the same Category.
""")

REQUIRED_HELP_TEXT = _("""

""")

TYPE_HELP_TEXT = _("""

""")

SUBSIDIARY_TYPE_HELP_TEXT = _("""

""")

MAJORITY_MINORITY_HELP_TEXT = _("""

""")

CERTAINTY_DEGREE_HELP_TEXT = _("""

""")

MAJORITY_CHOICES_HELP_TEXT = _("""
The backend of the site automatically records the most answered answers based on the existing answers. If you wish to display a majority-minority diagnostic when there are fewer than 10 existing answers, you can set it up here.
""")

HIDING_QUESTION_CATEGORY_ORDER_HELP_TEXT = _("""
If the question is a hidden question, then you can set the CATEGORY in which the question appears. (Note that the order of the CATEGORY prompts is randomized.)
""")

CATEGORY_HELP_TEXT = _("""
After creating a new CATEGORY, please click "Save" or "Save and continue editing" at the bottom of the page. The new CATEGORY will then appear in the options.
""")

NUMBER_OF_RESPONSES = _("""
Shows how many answers have been collected.
""")


MARKINGS = _("""
For questions created via CSV files, this identifier is used to identify the different questions. For questions created from pages, this identifier is not required.
""")

def validate_choices(choices):
    """Verifies that there is at least two choices in choices
    :param String choices: The string representing the user choices.
    """
    values = choices.split(settings.CHOICES_SEPARATOR)
    empty = 0
    for value in values:
        if value.replace(" ", "") == "":
            empty += 1
    if len(values) < 2 + empty:
        msg = "The selected field requires an associated list of choices."
        msg += " Choices must contain more than one item."
        raise ValidationError(msg)

def random_number():
    not_unique = True
    while not_unique:
        unique_ref = random.randint(100000, 999999)
        if not Question.objects.filter(random_order_q=unique_ref):
            not_unique = False
    return unique_ref


class SortAnswer:
    CARDINAL = "cardinal"
    ALPHANUMERIC = "alphanumeric"



class Question(models.Model):
    SELECT = "select"

    TEXT = "text"
    SHORT_TEXT = "short-text"
    RADIO = "radio"
    SELECT_IMAGE = "select_image"
    SELECT_MULTIPLE = "select-multiple"
    INTEGER = "integer"
    FLOAT = "float"
    DATE = "date"

    QUESTION_TYPES = (
        (SELECT, _("select")),
        (TEXT, _("text (multiple line)")),
        (SHORT_TEXT, _("short text (one line)")),
        (RADIO, _("radio")),
        (SELECT_MULTIPLE, _("Select Multiple")),
        (SELECT_IMAGE, _("Select Image")),
        (INTEGER, _("integer")),
        (FLOAT, _("float")),
        (DATE, _("date")),
    )

    MAJORITY_MINORITY = (
        ("majority", _("多数派")),
        ("minority", _("少数派")),
    )

    SUBSIDIARY_TYPE = (
        ("majority_minority",_("majority_minority")),
        ("certainty_degree",_("certainty_degree")),
    )
    markings = models.CharField(_("markings"), max_length=100, blank=True, null=True, help_text=MARKINGS)
    text = CKEditor5Field(_("Question Body"), blank=True, null=True, help_text=TYPE_HELP_TEXT, config_name='extends')
    # text = models.TextField(_("Text"), help_text=TEXT_HELP_TEXT)
    order = models.IntegerField(_("Order"), help_text=ORDER_HELP_TEXT, default=0)
    required = models.BooleanField(_("Required"), default=True, help_text=REQUIRED_HELP_TEXT)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, verbose_name=_("Category"),blank=True, null=True, related_name="questions", help_text=CATEGORY_HELP_TEXT
    )
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, blank=True, null=True, verbose_name=_("Survey"), related_name="questions")
    type = models.CharField(_("Type"), max_length=200, choices=QUESTION_TYPES, default=SELECT, help_text=TYPE_HELP_TEXT)
    choices = models.CharField(_("Choices"), blank=True, null=True, max_length=100, help_text=CHOICES_HELP_TEXT)
    subsidiary_type = models.CharField(_("subsidiary_type"), max_length=100, choices=SUBSIDIARY_TYPE, default="majority_minority", help_text=SUBSIDIARY_TYPE_HELP_TEXT)
    majority_minority = models.CharField(_("majority_minority"), max_length=200, choices=MAJORITY_MINORITY, default="majority", help_text=MAJORITY_MINORITY_HELP_TEXT)
    certainty_degree = models.IntegerField(_("degree of certainty"), default=50, help_text=CERTAINTY_DEGREE_HELP_TEXT)
    majority_choices = models.CharField(max_length=200, default="Null", help_text=MAJORITY_CHOICES_HELP_TEXT)
    hiding_question_category_order = models.IntegerField(_("Hiding question category order"), default=0, help_text=HIDING_QUESTION_CATEGORY_ORDER_HELP_TEXT)
    random_order_q = models.IntegerField(_("random_order_q"), blank=True, default=0)
    number_of_responses = models.IntegerField(_("number_of_responses"), default=0, help_text=NUMBER_OF_RESPONSES)
    jump_type = models.CharField(_("Jump Type"), default="no-jumping",blank=True,null=True,max_length=40)
    class Meta:
        verbose_name = _("question")
        verbose_name_plural = _("questions")
        ordering = ("survey", "order")

    def save(self, *args, **kwargs):
        if self.type in [Question.RADIO, Question.SELECT, Question.SELECT_MULTIPLE]:
            validate_choices(self.choices)
        super().save(*args, **kwargs)

    def get_clean_choices(self):
        """Return split and stripped list of choices with no null values."""
        if self.choices is None:
            return []
        choices_list = []
        for choice in self.choices.split(settings.CHOICES_SEPARATOR):
            choice = choice.strip()
            if choice:
                choices_list.append(choice)
        return choices_list

    @property
    def answers_as_text(self):
        """Return answers as a list of text.

        :rtype: List"""
        answers_as_text = []
        for answer in self.answers.all():
            for value in answer.values:
                answers_as_text.append(value)
        return answers_as_text

    @staticmethod
    def standardize(value, group_by_letter_case=None, group_by_slugify=None):
        """Standardize a value in order to group by slugify or letter case"""
        if group_by_slugify:
            value = slugify(value)
        if group_by_letter_case:
            value = value.lower()
        return value

    @staticmethod
    def standardize_list(string_list, group_by_letter_case=None, group_by_slugify=None):
        """Return a list of standardized string from a csv string.."""
        return [Question.standardize(strng, group_by_letter_case, group_by_slugify) for strng in string_list]

    def answers_cardinality(
        self,
        min_cardinality=None,
        group_together=None,
        group_by_letter_case=None,
        group_by_slugify=None,
        filter=None,
        other_question=None,
    ):
        """Return a dictionary with answers as key and cardinality (int or
            dict) as value

        :param int min_cardinality: The minimum of answer we need to take it
            into account.
        :param dict group_together: A dictionary of value we need to group
            together. The key (a string) is a placeholder for the list of value
            it represent (A list of string)
        :param boolean group_by_letter_case: If true we will group 'Aa' with
            'aa and 'aA'. You can use group_together as a placeholder if you
            want everything to be named 'Aa' and not 'aa'.
        :param boolean group_by_slugify: If true we will group 'Aé b' with
            'ae-b' and 'aè-B'. You can use group_together as a placeholder if
            you want everything to be named 'Aé B' and not 'ae-b'.
        :param list filter: We will exclude every string in this list.
        :param Question other_question: Instead of returning the number of
            person that answered the key as value, we will give the cardinality
            for another answer taking only the user that answered the key into
            account.
        :rtype: Dict"""
        if min_cardinality is None:
            min_cardinality = 0
        if group_together is None:
            group_together = {}
        if filter is None:
            filter = []
            standardized_filter = []
        else:
            standardized_filter = Question.standardize_list(filter, group_by_letter_case, group_by_slugify)
        if other_question is not None:
            if not isinstance(other_question, Question):
                msg = "Question.answer_cardinality expect a 'Question' for "
                msg += "the 'other_question' parameter and got"
                msg += f" '{other_question}' (a '{other_question.__class__.__name__}')"
                raise TypeError(msg)
        return self.__answers_cardinality(
            min_cardinality,
            group_together,
            group_by_letter_case,
            group_by_slugify,
            filter,
            standardized_filter,
            other_question,
        )

    def __answers_cardinality(
        self,
        min_cardinality,
        group_together,
        group_by_letter_case,
        group_by_slugify,
        filter,
        standardized_filter,
        other_question,
    ):
        """Return an ordered dict but the insertion order is the order of
        the related manager (ie question.answers).

        If you want something sorted use sorted_answers_cardinality with a set
        sort_answer parameter."""
        cardinality = OrderedDict()
        for answer in self.answers.all():
            for value in answer.values:
                value = self.__get_cardinality_value(value, group_by_letter_case, group_by_slugify, group_together)
                if value not in filter and value not in standardized_filter:
                    if other_question is None:
                        self._cardinality_plus_n(cardinality, value, 1)
                    else:
                        self.__add_user_cardinality(
                            cardinality,
                            answer.response.user,
                            value,
                            other_question,
                            group_by_letter_case,
                            group_by_slugify,
                            group_together,
                            filter,
                            standardized_filter,
                        )
        cardinality = self.filter_by_min_cardinality(cardinality, min_cardinality)
        if other_question is not None:
            self.__handle_other_question_cardinality(
                cardinality,
                filter,
                group_by_letter_case,
                group_by_slugify,
                group_together,
                other_question,
                standardized_filter,
            )
        return cardinality

    def filter_by_min_cardinality(self, cardinality, min_cardinality):
        if min_cardinality != 0:
            temp = {}
            for value in cardinality:
                if cardinality[value] < min_cardinality:
                    self._cardinality_plus_n(temp, "Other", cardinality[value])
                else:
                    temp[value] = cardinality[value]
            cardinality = temp
        return cardinality

    def __handle_other_question_cardinality(
        self,
        cardinality,
        filter,
        group_by_letter_case,
        group_by_slugify,
        group_together,
        other_question,
        standardized_filter,
    ):
        """Treating the value for Other question that were not answered in this question"""
        for answer in other_question.answers.all():
            for value in answer.values:
                value = self.__get_cardinality_value(value, group_by_letter_case, group_by_slugify, group_together)
                if value not in filter + standardized_filter:
                    if answer.response.user is None:
                        self._cardinality_plus_answer(cardinality, _(settings.USER_DID_NOT_ANSWER), value)

    def sorted_answers_cardinality(
        self,
        min_cardinality=None,
        group_together=None,
        group_by_letter_case=None,
        group_by_slugify=None,
        filter=None,
        sort_answer=None,
        other_question=None,
    ):
        """Mostly to have reliable tests, but marginally nicer too...

        The ordering is reversed for same cardinality value so we have aa
        before zz."""
        # pylint: disable=too-many-locals
        cardinality = self.answers_cardinality(
            min_cardinality, group_together, group_by_letter_case, group_by_slugify, filter, other_question
        )
        # We handle SortAnswer without enum because using "type" as a variable
        # name break the enum module and we want to use type in
        # answer_cardinality for simplicity
        possibles_values = [SortAnswer.ALPHANUMERIC, SortAnswer.CARDINAL, None]
        undefined = sort_answer is None
        user_defined = isinstance(sort_answer, dict)
        valid = user_defined or sort_answer in possibles_values
        if not valid:
            msg = "Unrecognized option '%s' for 'sort_answer': " % sort_answer
            msg += "use nothing, a dict (answer: rank),"
            for option in possibles_values:
                msg += f" '{option}', or"
            msg = msg[:-4]
            msg += ". We used the default cardinal sorting."
            LOGGER.warning(msg)
        if undefined or not valid:
            sort_answer = SortAnswer.CARDINAL
        sorted_cardinality = None
        if user_defined:
            sorted_cardinality = sorted(list(cardinality.items()), key=lambda x: sort_answer.get(x[0], 0))
        elif sort_answer == SortAnswer.ALPHANUMERIC:
            sorted_cardinality = sorted(cardinality.items())
        elif sort_answer == SortAnswer.CARDINAL:
            if other_question is None:
                sorted_cardinality = sorted(list(cardinality.items()), key=lambda x: (-x[1], x[0]))
            else:
                # There is a dict instead of an int
                sorted_cardinality = sorted(list(cardinality.items()), key=lambda x: (-sum(x[1].values()), x[0]))
        return OrderedDict(sorted_cardinality)

    def _cardinality_plus_answer(self, cardinality, value, other_question_value):
        """The user answered 'value' to our question and
        'other_question_value' to the other question."""
        if cardinality.get(value) is None:
            cardinality[value] = {other_question_value: 1}
        elif isinstance(cardinality[value], int):
            # Previous answer did not had an answer to other question
            cardinality[value] = {_(settings.USER_DID_NOT_ANSWER): cardinality[value], other_question_value: 1}
        else:
            if cardinality[value].get(other_question_value) is None:
                cardinality[value][other_question_value] = 1
            else:
                cardinality[value][other_question_value] += 1

    def _cardinality_plus_n(self, cardinality, value, n):
        """We don't know what is the answer to other question but the
        user answered 'value'."""
        if cardinality.get(value) is None:
            cardinality[value] = n
        else:
            cardinality[value] += n

    def __get_cardinality_value(self, value, group_by_letter_case, group_by_slugify, group_together):
        """Return the value we should use for cardinality."""
        value = Question.standardize(value, group_by_letter_case, group_by_slugify)
        for key, values in list(group_together.items()):
            grouped_values = Question.standardize_list(values, group_by_letter_case, group_by_slugify)
            if value in grouped_values:
                value = key
        return value

    def __add_user_cardinality(
        self,
        cardinality,
        user,
        value,
        other_question,
        group_by_letter_case,
        group_by_slugify,
        group_together,
        filter,
        standardized_filter,
    ):
        values = [_(settings.USER_DID_NOT_ANSWER)]
        for other_answer in other_question.answers.all():
            if user is None:
                break
            if other_answer.response.user == user:
                # We suppose there is only a response per user
                # Why would you want this info if it is
                # possible to answer multiple time ?
                values = other_answer.values
                break
        for other_value in values:
            other_value = self.__get_cardinality_value(
                other_value, group_by_letter_case, group_by_slugify, group_together
            )
            if other_value not in filter + standardized_filter:
                self._cardinality_plus_answer(cardinality, value, other_value)

    def get_choices(self):
        """
        Parse the choices field and return a tuple formatted appropriately
        for the 'choices' argument of a form widget.
        """
        choices_list = []
        for choice in self.get_clean_choices():
            choices_list.append((slugify(choice, allow_unicode=True), choice))
        choices_tuple = tuple(choices_list)
        return choices_tuple

    def get_choice_index(self, choice):
        choices_list=self.get_clean_choices()
        return str(choices_list.index(choice)+1)

    def __str__(self):
        msg = f"Question '{self.text}' "
        if self.required:
            msg += "(*) "
        msg += f"{self.get_clean_choices()}"
        return msg
