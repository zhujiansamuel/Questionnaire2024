import logging

from django.db import models

from django.utils.translation import gettext_lazy as _
from .category import Category
from .question import Question

LOGGER = logging.getLogger(__name__)


class Jumping_Question(models.Model):
    answer_order = models.IntegerField(_("Answer Order"),default=1)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, verbose_name=_("ブロック"), null=True, related_name="jumping"
    )
    jumping_question = models.ForeignKey(
        Question, on_delete=models.SET_NULL, verbose_name=_("Jumping Question"), null=True, related_name="jumping_question"
    )
    question = models.ForeignKey(
        Question, on_delete=models.SET_NULL, verbose_name=_("Question"), null=True, related_name="question"
    )

