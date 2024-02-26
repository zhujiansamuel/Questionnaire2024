import random
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .survey import Survey

def random_number_2(*args,**kwargs):
    random_order = kwargs.pop("random_order",None)
    hiding_question_order = kwargs.pop("hiding_question_order",None)
    start = int(kwargs.pop("start","100000"))
    end = int(kwargs.pop("end","999999"))
    not_unique = True
    while not_unique:
        unique_ref = random.randint(start, end)
        if random_order:
            if not Category.objects.filter(random_order=unique_ref):
                not_unique = False
        elif hiding_question_order:
            if not Category.objects.filter(hiding_question_order=unique_ref):
                not_unique = False
    return unique_ref

def random_number():
    not_unique = True
    while not_unique:
        unique_ref = random.randint(100000, 999999)
        if not Category.objects.filter(random_order=unique_ref):
            not_unique = False
    return unique_ref



class Category(models.Model):
    name = models.CharField(_("Name"), max_length=400)
    # ---->
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_("Survey"), related_name="categories")
    # ---->
    order = models.IntegerField(_("Display order"), blank=True, null=True)
    description = models.CharField(_("Description"), max_length=2000, blank=True, null=True)
    # random_order由100000开始意味着order字段具有优先性，被赋予order的类别总是优先显示（暂时这样吧）
    random_order = models.IntegerField(_("random order"),blank=False, default=random_number)
    display_num = models.IntegerField(_("Number of questions displayed"), blank=True, default=10)

    hiding_question_order = models.CharField(_("This determines whether the hidden question is displayed in the category (0) or where within the category of questions it is displayed."),blank=True, null=True, max_length=6, default="1|2")

    class Meta:
        # pylint: disable=too-few-public-methods
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    def __str__(self):
        return self.name

    def slugify(self):
        return slugify(str(self))
