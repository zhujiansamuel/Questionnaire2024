from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext
from django.shortcuts import redirect, render, reverse

def make_published(modeladmin, request, queryset):
    """
    Mark the given survey as published
    """
    count = queryset.update(is_published=True)
    message = ngettext(
        "%(count)d survey was successfully marked as published.",
        "%(count)d surveys were successfully marked as published",
        count,
    ) % {"count": count}
    modeladmin.message_user(request, message)

make_published.short_description = _("Mark selected surveys as published")


def add_question_button(self, request, queryset):
    survey_s = queryset.first()
    return redirect("add-question-with-id", id=survey_s.id)

def add_survey_button(self, request, queryset):
    pass


def survey_summary(self, request, queryset):
    survey_s = queryset.first()
    return redirect("surey-summary", survey_id=survey_s.id)