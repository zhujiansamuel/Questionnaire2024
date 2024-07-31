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

""")

DISPLAY_NUM_HELP_TEXT = _("""

""")

ORDER_HELP_TEXT = _("""

""")

DESCRIPTION_HELP_TEXT = _("""

""")

NAME_HELP_TEXT = _("""

""")

def random_number():
    not_unique = True
    while not_unique:
        unique_ref = random.randint(100000, 999999999)
        if not Category.objects.filter(name=unique_ref):
            not_unique = False
    return unique_ref

def col(ran):
    color_code_10 = str(ran)
    if len(color_code_10) < 9:
        add_0 = True
    else:
        add_0 = False
    while add_0:
        temp = list(color_code_10)
        temp.insert(0, "0")
        color_code_10 = ''.join(temp)
        if len(color_code_10) == 9:
            add_0 = False
    color_code_16_1 = int(int(color_code_10[:3]) / 3.917647058823529 / 51) * 51
    color_code_16_2 = int(int(color_code_10[3:6]) / 3.917647058823529 / 51) * 51
    color_code_16_3 = int(int(color_code_10[6:9]) / 3.917647058823529 / 51) * 51
    return '#%02x%02x%02x' % (color_code_16_1,color_code_16_2,color_code_16_3)

class Category(models.Model):
    ONE_Random = "one-random"
    SEQUENCE = "sequence"
    BRANCH = "branch"
    DEFAULT_Random = "default-random"
    CONTROL_QUESTION = "control-question"
    BLOCKTYPE = {
        (ONE_Random, _("グループ分け")),
        (SEQUENCE, _("順番固定")),
        (BRANCH, _("枝分かれ")),
        (DEFAULT_Random, _("デフォルト・ランダム")),
        (CONTROL_QUESTION, _("コントロール問題")),
    }
    
    name = models.CharField(_("Name"), max_length=400, default=random_number, help_text=NAME_HELP_TEXT)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_("調査セット"), related_name="categories")
    order = models.IntegerField(_("Display order"), blank=True, null=True, help_text=ORDER_HELP_TEXT)
    description = models.CharField(_("Description"), max_length=2000, blank=True, null=True, help_text=DESCRIPTION_HELP_TEXT)
    display_num = models.IntegerField(_("Number of questions displayed"), blank=True, default=999, help_text=DISPLAY_NUM_HELP_TEXT)
    hiding_question_order = models.CharField(_("Hiding question order"),blank=True, null=True, max_length=6, default="0", help_text=HIDING_QUESTION_ORDER_HELP_TEXT)
    block_type = models.CharField(_("ブロック・タイプ"), max_length=200, choices=BLOCKTYPE, default=DEFAULT_Random, help_text=BLOCK_TYPE_HELP_TEXT)
    color = models.CharField(max_length=200,blank=True, null=True)
    class Meta:
        # pylint: disable=too-few-public-methods
        verbose_name = _("ブロック")
        verbose_name_plural = _("ブロック")

    def save(self, *args, **kwargs):
        self.color = col(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def slugify(self):
        return slugify(str(self))
