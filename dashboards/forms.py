from django import forms
from django.forms import models, widgets, fields
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import ApplicationUser
from survey.models.jumping import Jumping_Question
from survey.models.question import Question
from survey.models.category import Category

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


class JumpingQuestionForm(models.ModelForm):

    class Meta:
        model = Jumping_Question


class CreateQuestionForm(models.ModelForm):

    class Meta:
        model = Question

class CreateCategoryForm(models.ModelForm):

    class Meta:
        model = Category

