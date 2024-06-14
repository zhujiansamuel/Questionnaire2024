from django import forms
from django.forms import models, widgets, fields
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import ApplicationUser
from survey.models.jumping import Jumping_Question
from survey.models.question import Question
from survey.models.category import Category
from survey.models.survey import Survey
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.translation import gettext_lazy as _


class ExperimenterCreationForm(UserCreationForm):
    # first_name = forms.CharField(max_length=30, required=True, help_text='Required. Enter your first name.')
    # last_name = forms.CharField(max_length=30, required=True, help_text='Required. Enter your last name.')

    class Meta:
        model = ApplicationUser
        fields = [
            'username',
            'email',
            'password1',
            'password2',
            # 'Gender',
            'affiliated_school',
            'field_1',
            'nicknames',
            # 'birthdays',
        ]



class ParticipantCreationForm(UserCreationForm):
    # first_name = forms.CharField(max_length=30, required=True, help_text='Required. Enter your first name.')
    # last_name = forms.CharField(max_length=30, required=True, help_text='Required. Enter your last name.')

    class Meta:
        model = ApplicationUser
        fields = [
            'username',
            'email',
            'password1',
            'password2',
            # 'Gender',
            # 'affiliated_school',
            # 'field_1',
            'nicknames',
            # 'birthdays',
        ]

class CreateSurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = [
            'name',
            'hide_name',
            'description',
            'is_published',
            'publish_date',
            'expire_date',
            'diagnostic_page_indexing',
            'download_top_number'
        ]
        labels = {
            'name': _('Survey Name'),
            'hide_name': _('Survey Hide Name'),
            'description': _('Survey Category'),
            'is_published': _('Is Published'),
            'publish_date': _('Publish Date'),
            'expire_date': _('Expire Date'),
            'diagnostic_page_indexing': _('Diagnostic Page Indexing'),
            'download_top_number': _('Download Top Number'),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        self.requests = kwargs.pop("requests")
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        survry = super().save(commit=False)
        if self.user.is_authenticated:
            survry.founder = self.user
        survry.save()
        return survry



class JumpingQuestionForm(models.ModelForm):

    class Meta:
        model = Jumping_Question
        fields = ["answer_order"]
        labels = {
            'answer_order': _('Answer order')
        }


class CreateQuestionForm(models.ModelForm):

    class Meta:
        model = Question
        fields = ['text', 'choices','category','order','majority_choices', 'number_of_responses','markings']
        labels = {
            'text': _('Text'),
            'choices': _('Choices'),
            'category': _('Category'),
            'order': _('Order'),
            'markings': _('Markings'),
        }

class CreateCategoryForm(models.ModelForm):

    class Meta:
        model = Category
        fields = ["block_type"]
        labels = {
            'block_type': _('Block type'),
        }



BLOCK_TYPE_HELP_TEXT = _("""

""")

class CreateEveryQuestionForm(forms.Form):
    ONE_Random = "one-random"
    SEQUENCE = "sequence"
    BRANCH = "branch"
    DEFAULT_Random = "default-random"
    BLOCKTYPE = {
        (ONE_Random, _("グループ分け")),
        (SEQUENCE, _("順番固定")),
        (BRANCH, _("枝分かれ")),
        (DEFAULT_Random, _("デフォルト・ランダム")),

    }
    block_type = forms.ChoiceField(label="ブロック・タイプ", choices=BLOCKTYPE, help_text=BLOCK_TYPE_HELP_TEXT)
