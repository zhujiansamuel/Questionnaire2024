from django.contrib import admin

from survey.actions import make_published, add_question_button, add_survey_button
from survey.exporter.csv import Survey2Csv
from survey.exporter.tex import Survey2Tex
from survey.models import Answer, Category, Question, Response, Survey
from dashboards.models import ApplicationUser
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

# from simpleui.admin import AjaxAdmin

class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "is_participant", "is_staff", "affiliated_school")
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
    ordering = ('category',"order")
    fieldsets = [
        ("Question Body", {
            'fields': ['text', 'choices', ],
        }),
        ("Question Information",{
            'fields': ['category','order'],
         }),
        ("hiding question", {
            'fields': ['hiding_question_category_order'],
         }),
        ("Answer situation",{
            'fields': ['majority_choices', 'number_of_responses','markings'],
         })
    ]
    extra = 0
    readonly_fields = ('majority_choices', "number_of_responses",'markings')

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

    list_display = ("name","hide_name", "number_of_question", "founder", "is_published", "expire_date")
    list_filter = ("is_published", "publish_date")
    ordering = ("name",)
    search_fields = ("name",)
    fieldsets = [
        ("General Information", {
            'description': 'The name of the survey and a brief description of that survey can be changed here.',
            'fields': ['name', 'description', 'founder'],
        }),

        ("Privilege Management", {
            'description': 'The name of the survey and a brief description of that survey can be changed here.',
            'fields': ['is_published', 'publish_date', 'expire_date'],
        }),

    ]
    readonly_fields = ('founder',)
    inlines = [CategoryInline, QuestionInline]
    actions = [add_survey_button, add_question_button, make_published, Survey2Csv.export_as_csv]

    add_survey_button.short_description = '新たな調査セットを作成する'
    add_survey_button.icon = 'fa-solid fa-file-circle-plus'
    add_survey_button.type = 'success'
    # add_survey_button.style = 'color:black;'
    add_survey_button.action_type = 0
    add_survey_button.action_url = '/dashboards/add-survey/'

    add_question_button.short_description = '質問を追加する'
    add_question_button.icon = 'fa-solid fa-list-check'
    add_question_button.type = 'warning'

    def has_add_permission(self, request):
        return False


    def save_model(self, request, obj, form, change):
        if not obj.founder:
            obj.founder = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        queryset = super(SurveyAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return queryset
        else:
            operator = request.user
            return queryset.filter(founder=operator)

class AnswerBaseInline(admin.StackedInline):
    max_num = 0
    fields = ["get_question_markings","get_question_text", "body", "subsidiary"]
    readonly_fields = ("get_question_markings","get_question_text", "body", "subsidiary")
    extra = 0
    model = Answer

    @admin.display(description='Question Text')
    def get_question_text(self, obj):
        return obj.question.text

    @admin.display(description='Question Marking')
    def get_question_markings(self, obj):
        return obj.question.markings

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

class ResponseAdmin(admin.ModelAdmin):
    list_display = ("interview_uuid", "survey", "created", "user", "DIAGNOSTIC_RESULT","Majority_Rate_num","Correctness_Rate_num")
    list_filter = ("survey", "created", "user", "DIAGNOSTIC_RESULT")
    ordering = ("Majority_Rate_num","Correctness_Rate_num")
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
            'fields': ['DIAGNOSTIC_RESULT', 'Majority_Rate_num', 'Correctness_Rate_num', 'number_of_questions',"survey_founder"]
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
                       'DIAGNOSTIC_RESULT',
                       'Majority_Rate_num',
                       'Correctness_Rate_num',
                       'number_of_questions',
                       "survey_founder",
                       )
    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        queryset = super(ResponseAdmin, self).get_queryset(request)

        if request.user.is_superuser:
            return queryset
        else:
            operator = request.user
            return queryset.filter(survey_founder=operator)


# admin.site.register(Question, QuestionInline)
# admin.site.register(Category, CategoryInline)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(Response, ResponseAdmin)


admin.site.site_title = "Questionnaire Management"
admin.site.site_header = "Questionnaire Management"

admin.site.unregister(Group)

admin.site.unregister(ApplicationUser)
admin.site.register(ApplicationUser, UserAdmin)
