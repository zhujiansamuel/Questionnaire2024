from django.contrib import admin

from survey.actions import make_published
from survey.exporter.csv import Survey2Csv
from survey.exporter.tex import Survey2Tex
from survey.models import Answer, Category, Question, Response, Survey
from dashboards.models import ApplicationUser
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

# from simpleui.admin import AjaxAdmin

class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email")
    # list_filter = ("survey", "created", "user")
    ordering = ("username",)
    fieldsets = None

    fields = ["username",
              "email",
              "Gender",
              "is_active",
              "is_staff",
              "date_joined",
              "last_login",
              "is_participant",
              'affiliated_school',
              'field_1',
              'nicknames'
              ]
    readonly_fields = ("date_joined", "last_login")


class QuestionInline(admin.StackedInline):
    model = Question
    ordering = ("order", 'category')
    # fields = ["text", "category", 'choices', 'majority_choices', 'hiding_question_category_order']
    fieldsets = [
        ("Edit Question", {
            'fields': ['text', 'choices', 'category', 'hiding_question_category_order', 'majority_choices'],
        }),
    ]
    extra = 0


    def get_formset(self, request, survey_obj, *args, **kwargs):
        formset = super().get_formset(request, survey_obj, *args, **kwargs)
        if survey_obj:
            formset.form.base_fields["category"].queryset = survey_obj.categories.all()
        return formset

#

class CategoryInline(admin.StackedInline):
    model = Category
    extra = 0
    fields = ['name', 'display_num', 'hiding_question_order', 'block_type', 'description']
    show_change_link = True



class SurveyAdmin(admin.ModelAdmin):
    list_display = ("name", "is_published", "description", "publish_date")
    list_filter = ("is_published", "publish_date")
    ordering = ("name",)
    search_fields = ("name",)
    fieldsets = [
        ("General Information", {
            'description': 'The name of the survey and a brief description of that survey can be changed here.',
            'fields': ['name', 'description', 'diagnosis_stages_qs_num', 'diagnostic_page_indexing'],
        }),

        ("Privilege Management", {
            'description': 'The name of the survey and a brief description of that survey can be changed here.',
            'fields': ['is_published', 'publish_date', 'expire_date'],
        }),
    ]

    inlines = [CategoryInline, QuestionInline]
    actions = [make_published, Survey2Csv.export_as_csv]


class AnswerBaseInline(admin.StackedInline):
    max_num = 0
    fields = ["get_question_text", "body", "subsidiary"]
    readonly_fields = ("get_question_text", "body", "subsidiary")
    extra = 0
    model = Answer

    @admin.display(description='Question Text')
    def get_question_text(self, obj):
        return obj.question.text

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

class ResponseAdmin(admin.ModelAdmin):
    list_display = ("interview_uuid", "survey", "created", "user", "repeat_order")
    list_filter = ("survey", "created", "user")
    date_hierarchy = "created"
    inlines = [AnswerBaseInline]
    fieldsets = [
        ("General Information", {
            'description': 'The ID is an administrative number within the site that is unique.',
            'fields': ['interview_uuid', 'created'],
        }),
        ('Related information', {
            'description': "Specific information can be viewed or edited by clicking on the survey name or user name.",
            'fields': ['survey', 'user'],
        }),
        ('Quick facts on statistics', {
            'description': "Majority-Rate and Correctness-Rate are automatically calculated by the website and are for reference only. As users are allowed to answer the questionnaire repeatedly, the answered questions will not be repeated.Order of repeated refers to the number of indexes of the same user's answers to the same questionnaire, which is only used for the internal management of the website.",
            'fields': ['Majority_Rate', 'Correctness_Rate', 'repeat_order']
        }),
    ]
    # specifies the order as well as which fields to act on
    readonly_fields = ("survey",
                       "created",
                       "interview_uuid",
                       "user",
                       "Majority_Rate",
                       "Correctness_Rate",
                       "repeat_order",
                       "completion_status",
                       )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


# admin.site.register(Question, QuestionInline)
# admin.site.register(Category, CategoryInline)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(Response, ResponseAdmin)


admin.site.site_title = "Questionnaire Management"
admin.site.site_header = "Questionnaire Management"

admin.site.unregister(Group)

admin.site.unregister(ApplicationUser)
admin.site.register(ApplicationUser, UserAdmin)
