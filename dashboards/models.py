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


    field_1_choice = {
        ("Philosophy", "Philosophy"),
        ("Sociology", "Sociology"),
        ("Psychology", "Psychology"),
        ("Economics", "Economics"),
        ("Education", "Education"),
        ("Information Science", "Information Science"),
        ("OTHER", "OTHER"),
    }


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
                              unique=False, blank=True, null=True)

    is_staff = models.BooleanField(
        _("Manage surveys."),
        default=False,
        help_text=_("Users who are authorized to administer surveys."),
    )

    affiliated_school = models.CharField(
        _("Affiliated School"),
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Affiliated School"),
    )

    field_1 = models.CharField(
        _("field (of study, etc.)"),
        choices=field_1_choice,
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Users who are authorized to administer surveys.(All users can answer the questionnaire.)"),
    )

    nicknames = models.CharField(
        _("Nicknames"),
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Nicknames"),
    )

    # birthdays = models.DateField(
    #     _("Birthdays"),
    #     auto_now=True,
    #     help_text=_("Birthdays"),
    # )


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


