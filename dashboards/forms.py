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
from django_ckeditor_5.widgets import CKEditor5Widget
from django.utils.translation import gettext_lazy as _
from django.forms import formset_factory


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
        widgets = {

            "publish_date": widgets. DateInput(),
            "expire_date": widgets.DateInput(),

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

class CreateQuestionForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ['text', 'choices','order']
        labels = {
            'text': _('Text'),
            'choices': _('Choices'),
            'order': _('Order'),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        self.requests = kwargs.pop("requests")
        self.survey = kwargs.pop("survey")
        super().__init__(*args, **kwargs)



BLOCK_TYPE_HELP_TEXT = _("""

""")

class CreateEveryQuestionForm(forms.Form):
    Q1 = "1"
    Q2 = "2"
    Q3 = "3"
    Q4 = "4"
    JUMPING_CHOICES = (
        (Q1, _("1")),
        (Q2, _("2")),
        (Q3, _("3")),
        (Q4, _("4")),
    )
    # -------------------------------------------
    # -------------------------------------------
    question_text = forms.CharField(label=_('Question Body'), widget=CKEditor5Widget())
    question_choices = forms.CharField(label=_('Question Choices'))
    # -------------------------------------------
    # -------------------------------------------
    jumping_1_choices_order = forms.ChoiceField(label=_('Choices Order'),choices=JUMPING_CHOICES, initial='1',required=False)
    jumping_1_question_text = forms.CharField(label=_('Question 1 Body'), widget=CKEditor5Widget())
    jumping_1_question_choices = forms.CharField(label=_('Question 1 Choices'))
    # -------------------------------------------
    jumping_2_choices_order = forms.ChoiceField(label=_('Choices Order'),choices=JUMPING_CHOICES, initial='2',required=False)
    jumping_2_question_text = forms.CharField(label=_('Question 2 Body'), widget=CKEditor5Widget(),required=False)
    jumping_2_question_choices = forms.CharField(label=_('Question 2 Choices'),required=False)
    # -------------------------------------------
    jumping_3_choices_order = forms.ChoiceField(label=_('Choices Order'),choices=JUMPING_CHOICES, initial='3',required=False)
    jumping_3_question_text = forms.CharField(label=_('Question 3 Body'), widget=CKEditor5Widget(),required=False)
    jumping_3_question_choices = forms.CharField(label=_('Question 3 Choices'),required=False)
    # -------------------------------------------
    jumping_4_choices_order = forms.ChoiceField(label=_('Choices Order'),choices=JUMPING_CHOICES, initial='4',required=False)
    jumping_4_question_text = forms.CharField(label=_('Question 4 Body'), widget=CKEditor5Widget(),required=False)
    jumping_4_question_choices = forms.CharField(label=_('Question 4 Choices'),required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)





class CreateDefaultRandomForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["text"].required = False
    class Meta:
        model = Question
        fields = ['text', 'choices']
        labels = {
            'text': _('Text'),
            'choices': _('Choices'),
        }
        widgets = {
            "text": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="extends"
            )
        }


