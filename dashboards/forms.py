from django import forms
from django.forms import models, widgets, fields
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import ApplicationUser
from survey.models.jumping import Jumping_Question
from survey.models.question import Question
from survey.models.category import Category
from survey.models.survey import Survey
from survey.models.global_variable import GlobalVariable
from django_ckeditor_5.fields import CKEditor5Field
from django_ckeditor_5.widgets import CKEditor5Widget
from django.utils.translation import gettext_lazy as _
from django.forms import formset_factory
from django.core.exceptions import ValidationError

from django import forms

class ListTextWidget(forms.TextInput):
    def __init__(self, data_list, name, *args, **kwargs):
        super(ListTextWidget, self).__init__(*args, **kwargs)
        self._name = name
        self._list = data_list
        self.attrs.update({'list':'list__%s' % self._name})

    def render(self, name, value, attrs=None, renderer=None):
        text_html = super(ListTextWidget, self).render(name, value, attrs=attrs)
        data_list = '<datalist id="list__%s">' % self._name
        for item in self._list:
            data_list += '<option value="%s">' % item
        data_list += '</datalist>'

        return (text_html + data_list)


class GlobalSetupForm(forms.Form):
    # number_of_responses = forms.IntegerField(label="?")
    diagnostic_page_indexing = forms.IntegerField(
        label="診断結果の表示の最低数",
        help_text='質問の回答数がこの値より多い場合のみ、正解/不正解の結果が表示される。'
    )
    # download_top_number = forms.IntegerField(label="最高点数の回答をダウンロードする数")
    number_of_question = forms.IntegerField(
        label="調査セットの問題の最低数",
        help_text='質問数がこの値より多い場合のみ、調査セットが公開される。'
    )




class ExperimenterCreationForm(UserCreationForm):
    # first_name = forms.CharField(max_length=30, required=True, help_text='Required. Enter your first name.')
    # last_name = forms.CharField(max_length=30, required=True, help_text='Required. Enter your last name.')
    extra_field = forms.CharField(required=False)

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
            # 'nicknames',
            # 'birthdays',
        ]

    def clean_email(self):
        email_data = self.cleaned_data.get("email")
        if ApplicationUser.objects.filter(email=email_data).exists():
            raise ValidationError("This email is already in use.")
        return email_data


class ParticipantCreationForm(UserCreationForm):
    # first_name = forms.CharField(max_length=30, required=True, help_text='Required. Enter your first name.')
    # last_name = forms.CharField(max_length=30, required=True, help_text='Required. Enter your last name.')

    class Meta:
        model = ApplicationUser
        fields = [
            'username',
            # 'email',
            'password1',
            'password2',
            # 'Gender',
            # 'affiliated_school',
            # 'field_1',
            'nicknames',
            # 'birthdays',
        ]

    def clean_nicknames(self):
        nicknames = self.cleaned_data.get("nicknames")
        if ApplicationUser.objects.filter(nicknames=nicknames).exists():
            raise ValidationError("This nicknames is already in use")
        return nicknames

class CreateSurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = [
            'name',
            'hide_name',
            'description',
            # 'is_published',
            # 'publish_date',
            # 'expire_date',
            # 'diagnostic_page_indexing',
            # 'download_top_number'
        ]
        labels = {
            'name': _('ゲームの名前'),
            'hide_name': _('管理用の名前'),
            'description': _('カテゴリー'),
            # 'is_published': _('Is Published'),
            # 'publish_date': _('Publish Date'),
            # 'expire_date': _('Expire Date'),
            # 'diagnostic_page_indexing': _('Diagnostic Page Indexing'),
            # 'download_top_number': _('Download Top Number'),
        }
        # widgets = {
        #     "publish_date": widgets. DateInput(),
        #     "expire_date": widgets.DateInput(),
        # }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        self.requests = kwargs.pop("requests")
        super().__init__(*args, **kwargs)


    def clean_name(self):
        name = self.cleaned_data.get("name")
        if Survey.objects.filter(name=name).exists():
            raise ValidationError("This name is already in use.")
        return name

    def clean_hide_name(self):
        hide_name = self.cleaned_data.get("hide_name")
        if Survey.objects.filter(hide_name=hide_name).exists():
            raise ValidationError("This hide-name already in use.")
        return hide_name

    def save(self, commit=True):
        survry = super().save(commit=False)
        if self.user.is_authenticated:
            survry.founder = self.user
        survry.save()
        return survry



class CreateQuestionForm(forms.ModelForm):
    choice_1_field = forms.CharField(label="選択肢１", required=True)
    choice_2_field = forms.CharField(label="選択肢２", required=True)

    class Meta:
        model = Question
        fields = ['text', ]
        labels = {
            'text': _('Text'),
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
    # Q3 = "3"
    # Q4 = "4"
    JUMPING_CHOICES = (
        (Q1, _("1")),
        (Q2, _("2")),
        # (Q3, _("3")),
        # (Q4, _("4")),
    )
    # -------------------------------------------
    # -------------------------------------------
    question_text = forms.CharField(label=_('Text'), widget=CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="extends"),required=False)
    choice_1_field = forms.CharField(label=_('選択肢１'), widget=forms.Textarea(attrs={"class": "choice-field",}), required=True)
    choice_2_field = forms.CharField(label=_('選択肢２'), widget=forms.Textarea(attrs={"class": "choice-field",}), required=True)

    # -------------------------------------------
    # -------------------------------------------
    jumping_1_choices_order = forms.ChoiceField(label=_('Choices Order'),choices=JUMPING_CHOICES, initial='1',required=False)
    jumping_1_question_text = forms.CharField(label=_('Question 1 Text'), widget=CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="extends"),required=False)
    jumping_1_choice_1_field = forms.CharField(label=_('選択肢１'), widget=forms.Textarea(attrs={"class": "choice-field",}), required=True)
    jumping_1_choice_2_field = forms.CharField(label=_('選択肢２'),
                                               widget=forms.Textarea(attrs={"class": "choice-field", }), required=True)

    # -------------------------------------------
    jumping_2_choices_order = forms.ChoiceField(label=_('Choices Order'),choices=JUMPING_CHOICES, initial='2',required=False)
    jumping_2_question_text = forms.CharField(label=_('Question 2 Text'), widget=CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="extends"),required=False)
    jumping_2_choice_1_field = forms.CharField(label=_('選択肢１'), widget=forms.Textarea(attrs={"class": "choice-field",}), required=True)
    jumping_2_choice_2_field = forms.CharField(label=_('選択肢２'),
                                               widget=forms.Textarea(attrs={"class": "choice-field", }), required=True)
    # # -------------------------------------------
    # jumping_3_choices_order = forms.ChoiceField(label=_('Choices Order'),choices=JUMPING_CHOICES, initial='3',required=False)
    # jumping_3_question_text = forms.CharField(label=_('Question 3 Body'), widget=CKEditor5Widget(),required=False)
    # jumping_3_question_choices = forms.CharField(label=_('Question 3 Choices'),required=False)
    # # -------------------------------------------
    # jumping_4_choices_order = forms.ChoiceField(label=_('Choices Order'),choices=JUMPING_CHOICES, initial='4',required=False)
    # jumping_4_question_text = forms.CharField(label=_('Question 4 Body'), widget=CKEditor5Widget(),required=False)
    # jumping_4_question_choices = forms.CharField(label=_('Question 4 Choices'),required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class InputExtraNum(forms.Form):
    Q2 = "2"
    Q3 = "3"
    Q4 = "4"
    Q5 = "5"
    Q6 = "6"
    Q7 = "7"
    Q8 = "8"
    Q9 = "9"
    Q10 = "10"
    NUM_CHOICES = (
        (Q2, _("2")),
        (Q3, _("3")),
        (Q4, _("4")),
        (Q5, _("5")),
        (Q6, _("6")),
        (Q7, _("7")),
        (Q8, _("8")),
        (Q9, _("9")),
        (Q10, _("10")),
    )
    num = forms.ChoiceField(label=_("質問数"),choices=NUM_CHOICES, initial=Q2, required=False)



class CreateDefaultRandomForm(forms.ModelForm):
    choice_1_field = forms.CharField(label="選択肢１", required=True)
    choice_2_field = forms.CharField(label="選択肢２", required=True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["choice_1_field"].widget = forms.Textarea(attrs={
            "class": "choice-field",
        })
        self.fields["choice_2_field"].widget = forms.Textarea(attrs={
            "class": "choice-field",
        })
        self.fields["text"].required = False
    class Meta:
        model = Question
        fields = ['text']
        labels = {
            'text': _('Text'),
        }
        widgets = {
            "text": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="extends"
            ),
        }


