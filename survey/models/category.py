import random
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .survey import Survey

HIDING_QUESTION_ORDER_HELP_TEXT = """
This determines whether the hidden question is displayed in the category.
There is not hiding question when sitting 0.
If there are multiple locations where hidden questions need to be inserted, please use "|" to separate them. 
For example, "1 | 3" indicates that the first and third questions are hidden questions.
"""

BLOCK_TYPE_HELP_TEXT = _("""
 There are two types of CATEGORY: "sequence" and "one-random". The "sequence" type of CATEGORY will display the questions in order. A "one-random" CATEGORY will display a random question from that CATEGORY.
""")

DISPLAY_NUM_HELP_TEXT = _("""
Sets the number of questions under the CATEGORY. If this number is greater than the total number of questions under the CATEGORY, all questions under the CATEGORY will be displayed. (CATEGORY of type "one-random" are not affected by this setting.)
""")

ORDER_HELP_TEXT = _("""

""")

DESCRIPTION_HELP_TEXT = _("""

""")

NAME_HELP_TEXT = _("""
If you want the survey to contain hidden questions, then create a CATEGORY called "hiding_question".
""")

def random_number():
    not_unique = True
    while not_unique:
        unique_ref = random.randint(100000, 999999)
        if not Category.objects.filter(random_order=unique_ref):
            not_unique = False
    return unique_ref



class Category(models.Model):
    ONE_Random = "one-random"
    SEQUENCE = "sequence"
    BLOCKTYPE = {
        (ONE_Random, _("one-random")),
        (SEQUENCE, _("sequence"))
    }
    
    name = models.CharField(_("Name"), max_length=400, help_text=NAME_HELP_TEXT)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_("Survey"), related_name="categories")
    order = models.IntegerField(_("Display order"), blank=True, null=True, help_text=ORDER_HELP_TEXT)
    description = models.CharField(_("Description"), max_length=2000, blank=True, null=True, help_text=DESCRIPTION_HELP_TEXT)
    display_num = models.IntegerField(_("Number of questions displayed"), blank=True, default=10, help_text=DISPLAY_NUM_HELP_TEXT)
    hiding_question_order = models.CharField(_("Hiding question order"),blank=True, null=True, max_length=6, default="0", help_text=HIDING_QUESTION_ORDER_HELP_TEXT)
    block_type = models.CharField(_("Block type"), max_length=200, choices=BLOCKTYPE, default=SEQUENCE, help_text=BLOCK_TYPE_HELP_TEXT)
    class Meta:
        # pylint: disable=too-few-public-methods
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    def __str__(self):
        return self.name

    def slugify(self):
        return slugify(str(self))
