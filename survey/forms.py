import logging
import uuid
import random
from django import forms
from random import choice
from django.conf import settings
from django.forms import models, widgets, fields
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect
from django.core.cache import cache


from survey.models import Answer, Category, Question, Response, Survey
from survey.signals import survey_completed
from survey.widgets import ImageSelectWidget

from survey.utility.recalculated_results import calculate_results

LOGGER = logging.getLogger(__name__)

class UploadFileForm(forms.Form):
    # title = forms.CharField(max_length=50)
    file = forms.FileField()

class ResponseForm(models.ModelForm):

    FIELDS = {
        Question.TEXT: forms.CharField,
        Question.SHORT_TEXT: forms.CharField,
        Question.SELECT_MULTIPLE: forms.MultipleChoiceField,
        Question.INTEGER: forms.IntegerField,
        Question.FLOAT: forms.FloatField,
        Question.DATE: forms.DateField,
    }

    WIDGETS = {
        Question.TEXT: forms.Textarea,
        Question.SHORT_TEXT: forms.TextInput,
        Question.RADIO: forms.RadioSelect,
        Question.SELECT: forms.Select,
        Question.SELECT_IMAGE: ImageSelectWidget,
        Question.SELECT_MULTIPLE: forms.CheckboxSelectMultiple,
    }

    class Meta:
        model = Response
        fields = ()

    def __init__(self, *args, **kwargs):
        """Expects a survey object to be passed in initially"""
        flat = lambda L: sum(map(flat, L), []) if isinstance(L, list) else [L]
        self.survey = kwargs.pop("survey")
        self.user = kwargs.pop("user")
        self.requests = kwargs.pop("requests")
        self.session_random_list = kwargs.pop("session_random_list")
        #
        try:
            self.step = int(kwargs.pop("step"))
        except KeyError:
            self.step = None
        super().__init__(*args, **kwargs)
        self.uuid = uuid.uuid4().hex

        session_key = "survey_{}".format(self.survey.id)
        diagnostic_session_key = "diagnostic_{}_{}".format(self.requests.user, self.survey.name)
        if self.step == 0:
            try:
                temp = self.requests.session[diagnostic_session_key]
            except:
                pass
            else:
                del self.requests.session[diagnostic_session_key]

            try:
                temp = self.requests.session[session_key]
            except:
                pass
            else:
                del self.requests.session[session_key]

        self.response = False
        self.answers = False
        # 注意：self._get_preexisting_response()方法内部直接设定self.response
        self.preexisting_response = self._get_preexisting_response()
        # TranslateComments
        # 以下内容用于实现产生新的response
        # -------------------------------------------------------------------

        if self.response and self.response.count() > 1:
            repeat_order_list = [int(response_temp.repeat_order) for response_temp in self.response]
            self.repeat_order = max(repeat_order_list) + 1
            self.response = None
        elif self.response and self.response.count() == 1:
            self.repeat_order = 1
            self.response = None
        else:
            self.repeat_order = 0

        # -------------------------------------------------------------------
        # -------------------------------------------------------------------

        # print(" ----------------------已经回答的问题-------------------------- ")
        self.questions_answered = []
        if self.preexisting_response.count() > 1:
            for response_temp in self.preexisting_response:
                answers = Answer.objects.filter(response_id=response_temp.id).prefetch_related("question")
                if answers.count() > 1:
                    questions_a = [q.question for q in answers]
                elif answers.count() == 1:
                    questions_a = answers.first().question
                else:
                    questions_a = []
                self.questions_answered.append(questions_a)
        elif self.preexisting_response.count() == 1:
            answers = Answer.objects.filter(response_id=self.preexisting_response.first().id).prefetch_related("question")
            if answers.count() > 1:
                questions_a = [q.question for q in answers]
            elif answers.count() == 1:
                questions_a = answers.first().question
            else:
                questions_a = []
            self.questions_answered.append(questions_a)

        if self.questions_answered:
            self.questions_answered = flat(list(self.questions_answered))


        # -------------------------------------------------------------------
        # TranslateComments
        # 以下的内容设定了每个调查问卷中的问题设置
        # -------------------------------------------------------------------
        # TranslateComments
        # 初始化会话随机列表

        self.categories = []
        categories_s = self.survey.random_categories()
        categories_dic = {}
        for i, category in enumerate(categories_s):
            random_order = self.session_random_list[str(i+1)]
            categories_dic[random_order] = category
        categories_dic_sorted = sorted(categories_dic.items(), key=lambda x:x[0] )
        self.categories = [v for i, v in categories_dic_sorted]


        # -------------------------------------------------------------------
        # -------------------------------------------------------------------
        self.qs_with_no_cat = self.survey.questions.filter(category__isnull=True).order_by("order", "id")
        if self.qs_with_no_cat:
            self.qs_with_no_cat = self.eliminate_answered_questions(self.self.qs_with_no_cat)

        # -------------------------------------------------------------------
        # -------------------------------------------------------------------
        self.hiding_question = []
        # TranslateComments
        # 获取隐藏问题，它们将被安插进允许由隐藏问题的类别中
        self.hiding_question_category = [x for x in list(self.survey.categories.order_by("id")) if x.name == "hiding_question"]
        self.hiding_question_category = self.eliminate_answered_questions(self.hiding_question_category)
        if self.hiding_question_category:
            self.hiding_question = list(self.hiding_question_category[0].questions.order_by("-hiding_question_category_order"))
            self.hiding_question = self.eliminate_answered_questions(self.hiding_question)
        else:
            self.hiding_question = []


        # -------------------------------------------------------------------
        # -------------------------------------------------------------------

        self.question_to_display = []
        # TranslateComments
        # self.question_to_display是可以显示在调查问卷中的问题的list
        for i_category, category in enumerate(self.categories):
            category_question_all = self.eliminate_answered_questions(category.questions.all())
            if category.block_type == "sequence":
                # TranslateComments
                # 对于1类类别，可加入隐藏问题
                # 隐藏类别的问题并不会独立显示而是根据category.hiding_question_order决定放在该类别的那个位置
                # 隐藏问题在第几个block中显示由question.hiding_question_category_order设定
                if category.display_num <= len(category_question_all):
                    # TranslateComments
                    # 如果设置的显示数量小于或者等于问题数目，那么按照设定的显示数量显示问题
                    question_s = category_question_all[:int(category.display_num)]
                elif category.display_num > len(category_question_all):
                    # TranslateComments
                    # 如果设置的显示数量大于问题数目，那么显示全部的问题，忽略设定的显示数量
                    question_s = category_question_all

                else:
                    question_s = []
                if category.hiding_question_order and self.hiding_question:
                    # TranslateComments
                    # 如果该类别允许添加隐藏问题，以及有隐藏问题可以添加
                    question_add = []
                    if "|" in category.hiding_question_order:
                        # TranslateComments
                        # 如果该类别中需要添加多个隐藏问题
                        orders = category.hiding_question_order.split("|")
                        orders_int = []
                        orders_within = []
                        for ord in orders:
                            try:
                                order_int = int(ord)
                            except ValueError:
                                continue
                            else:
                                if order_int < len(question_s):
                                    orders_within.append(order_int)
                                else:
                                    orders_int.append(order_int)
                        for i, question in enumerate(question_s):
                            for order in orders_within:
                                if i + 1 == order:
                                    try:
                                        hq = self.hiding_question.pop()
                                    except IndexError:
                                        pass
                                    else:
                                        question_add.append(hq)

                            question_add.append(question)
                        if orders_int:
                            for ord in orders_int:
                                try:
                                    hq = self.hiding_question.pop()
                                except IndexError:
                                    pass
                                else:
                                    question_add.append(hq)
                    elif "|" not in category.hiding_question_order:
                        # TranslateComments
                        # 如果该类别中只添加一个隐藏问题
                        try:
                            order = int(category.hiding_question_order)
                        except ValueError:
                            pass
                        else:
                            if order <= len(question_s):
                                for i, question in enumerate(question_s):
                                    if i + 1 == order:
                                        try:
                                            hq = self.hiding_question.pop()
                                        except IndexError:
                                            pass
                                        else:
                                            question_add.append(hq)
                                    question_add.append(question)
                            else:
                                question_add += question_s
                                try:
                                    hq = self.hiding_question.pop()
                                except IndexError:
                                    pass
                                else:
                                    # print(question_add)
                                    # print(hq)
                                    question_add.append(hq)
                    # TranslateComments
                    # 汇总各类别的问题，形成最终的调查问题列表
                    self.question_to_display += question_add
                else:
                    self.question_to_display += question_s
            elif category.block_type == "one-random":
                # TranslateComments
                # 对于2类类别，只加入类别中的一个问题
                # 同时保留添加隐藏问题的可能
                # 由category.hiding_question_order判定是否需要添加隐藏问题
                # category.hiding_question_order为0的时候意味着该类别中不添加隐藏问题
                all_question = self.eliminate_answered_questions(category.questions.all())
                # print("-->all_question:",all_question)
                # print(category.questions.all())
                # ----->
                random_question_dic = {}
                for i, question in enumerate(all_question):
                    random_order = self.session_random_list[str(i + 10)]
                    random_question_dic[random_order] = question
                random_question_dic_sorted = sorted(random_question_dic.items(), key=lambda x: x[0])
                # print("-->random_question_dic_sorted:",random_question_dic_sorted)
                if isinstance(random_question_dic_sorted, list):
                    if len(random_question_dic_sorted) > 1:
                        random_question = [v for i, v in random_question_dic_sorted][0]
                    elif len(random_question_dic_sorted) == 1:
                        random_question = random_question_dic_sorted[0][1]
                    else:
                        random_question = []
                # print("-->random_question:", random_question)
                question_add = []
                # TranslateComments
                # 允许在2类类别中添加隐藏问题，但是隐藏问题默认添加在第一或者第二（只有一个隐藏问题）第三位置（有两个隐藏问题）
                if category.hiding_question_order and self.hiding_question:
                    if "|" in category.hiding_question_order:
                        # TranslateComments
                        # 如果该类别中需要添加多个隐藏问题
                        orders = category.hiding_question_order.split("|")
                        orders_int = []

                        for ord in orders:
                            try:
                                order_int = int(ord)
                            except ValueError:
                                continue
                            else:
                                orders_int.append(order_int)
                        orders_int.sort()
                        continue_add = True
                        add_order = 1
                        with continue_add:
                            for order in orders_int:
                                if add_order == order:
                                    try:
                                        hq = self.hiding_question.pop()
                                    except IndexError:
                                        pass
                                    else:
                                        question_add.append(hq)
                                        orders_int = list(filter(lambda x: x != add_order, orders_int))
                                        if add_order+1 not in orders_int:
                                            question_add.append(random_question)
                            add_order += 1
                            if len(orders) == 0:
                                continue_add = False
                        question_add = list(filter(lambda x: x != [], question_add))
                    elif "|" not in category.hiding_question_order:
                        # TranslateComments
                        # 如果该类别中只添加一个隐藏问题
                        try:
                            order = int(category.hiding_question_order)
                        except ValueError:
                            pass
                        else:
                            try:
                                hq = self.hiding_question.pop()
                            except IndexError:
                                pass
                            else:
                                if order == 1:
                                    question_add.append(hq)
                                    question_add.append(random_question)
                                else:
                                    question_add.append(random_question)
                                    question_add.append(hq)
                    self.question_to_display += question_add
                else:
                    if random_question:
                        self.question_to_display.append(random_question)
        if self.qs_with_no_cat:
            self.question_to_display.append(self.qs_with_no_cat)
        self.question_to_display = flat(self.question_to_display)


        # -------------------------------------------------------------------
        # -------------------------------------------------------------------

        # -------------------------------------------------------------------
        if self.step == 0:
            print(" ------------------------------------------------------------ ")
            print("生成的问题")
            print(" -------- ")
            for i, question in enumerate(self.question_to_display):
                print("生成的问题  ", str(i), " :", question.text, "    ", question.category.name)
            print(" ------------------------------------------------------------ ")
        # -------------------------------------------------------------------
        # TranslateComments
        print(" ------------------------------------------------------------ ")
        print("Step:", self.step)
        print(" ------------------------------------------------------------ ")

        if self.survey.display_method == Survey.BY_CATEGORY:
            pass
            # self.steps_count = len(self.categories) + (1 if self.qs_with_no_cat else 0)
        else:
            self.steps_count = len(self.question_to_display)
        # -------------------------------------------------------------------

        self.add_questions(kwargs.get("data"))

    def eliminate_answered_questions(self, question_sequence):
        return [q for q in question_sequence if q not in self.questions_answered]



    def add_questions(self, data):
        # add a field for each survey question, corresponding to the question
        # type as appropriate.
        # -------------------------------------------------------------------
        if self.survey.display_method == Survey.BY_CATEGORY and self.step is not None:
            pass
        else:
            for i, question in enumerate(self.question_to_display):
                not_to_keep = i != self.step and self.step is not None
                if self.survey.display_method == Survey.BY_QUESTION and not_to_keep:
                    continue
                self.add_question(question, data)

    def current_categories(self):
        if self.survey.display_method == Survey.BY_CATEGORY:
            pass
        else:
            extras = []
            if self.qs_with_no_cat:
                extras = [Category(name="No category", description="No cat desc")]

            return self.categories + extras + self.hiding_question_category

    def _get_preexisting_response(self):
        """Recover a pre-existing response in database.

        The user must be logged. Will store the response retrieved in an attribute
        to avoid multiple db calls.

        :rtype: Response or None"""
        if self.response:
            return self.response

        if not self.user.is_authenticated:
            self.response = None
        else:
            try:
                self.response = Response.objects.prefetch_related("user", "survey").filter(
                    user=self.user, survey=self.survey
                )
            except Response.DoesNotExist:
                LOGGER.debug("No saved response for '%s' for user %s", self.survey, self.user)
                self.response = None
        return self.response

    def _get_preexisting_answers(self):
        """Recover pre-existing answers in database.

        The user must be logged. A Response containing the Answer must exists.
        Will create an attribute containing the answers retrieved to avoid multiple
        db calls.

        :rtype: dict of Answer or None"""
        if self.answers:
            return self.answers

        response = self._get_preexisting_response()
        if response is None:
            self.answers = None
        try:
            answers = Answer.objects.filter(response=response).prefetch_related("question")
            self.answers = {answer.question.id: answer for answer in answers.all()}
        except Answer.DoesNotExist:
            self.answers = None

        return self.answers

    def _get_preexisting_answer(self, question):
        answers = self._get_preexisting_answers()
        return answers.get(question.id, None)

    def get_question_initial(self, question, data):
        initial = None
        if data:
            # Initialize the field field from a POST request, if any.
            # Replace values from the database
            initial = data.get("question_%d" % question.pk)
        return initial

    def get_question_widget(self, question):
        try:
            return self.WIDGETS[question.type]
        except KeyError:
            return None

    @staticmethod
    def get_question_choices(question):
        qchoices = None
        if question.type not in [Question.TEXT, Question.SHORT_TEXT, Question.INTEGER, Question.FLOAT, Question.DATE]:
            qchoices = question.get_choices()
            # add an empty option at the top so that the user has to explicitly
            # select one of the options
            if question.type in [Question.SELECT, Question.SELECT_IMAGE]:
                qchoices = tuple([("", "-------------")]) + qchoices
        return qchoices

    def get_question_field(self, question, **kwargs):
        """Return the field we should use in our form.

        :param Question question: The question
        :param **kwargs: A dict of parameter properly initialized in
            add_question.
        :rtype: django.forms.fields"""
        # logging.debug("Args passed to field %s", kwargs)
        try:
            return self.FIELDS[question.type](**kwargs)
        except KeyError:
            return forms.ChoiceField(**kwargs)

    def add_question(self, question, data):
        MAJORITY_MINORITY = (
            ("majority", _("多数派")),
            ("minority", _("少数派")),
        )
        kwargs = {"label": question.text, "required": question.required, "help_text": question.subsidiary_type}
        choices = self.get_question_choices(question)
        if choices:
            kwargs["choices"] = choices
        widget = self.get_question_widget(question)
        if widget:
            kwargs["widget"] = widget

        field = self.get_question_field(question, **kwargs)
        field.widget.attrs["category"] = question.category.name if question.category else ""

        if question.type == Question.DATE:
            field.widget.attrs["class"] = "date"
        # logging.debug("Field for %s : %s", question, field.__dict__)
        self.fields["question_%d" % question.pk] = field

        if question.subsidiary_type == "majority_minority":
            subsidiary_question = fields.ChoiceField(choices=MAJORITY_MINORITY,
                                       label="この質問で、あなたが答えた回答は多数派だと想いますか、少数派だと思いますか？")
        else:
            subsidiary_question = fields.IntegerField(label="確信度？",initial=50)

        self.fields["question_subsidiary_%d" % question.pk] = subsidiary_question
        self.fields["question_subsidiary_%d" % question.pk].widget.attrs["category"] = question.category.name if question.category else ""

    def has_next_step(self):
        if not self.survey.is_all_in_one_page():
            if self.step < self.steps_count - 1:
                return True
        return False

    def next_step_url(self):
        if self.has_next_step():
            step_cache_key = "step_{}_{}".format(self.user,self.survey)
            step_cache = cache.get(step_cache_key)
            if step_cache is None and self.step==0:
                cache.set(step_cache_key, 1)
            elif step_cache:
                cache.set(step_cache_key, int(step_cache)+1)
            context = {"id": self.survey.id, "step": self.step + 1}
            return reverse("survey-detail-step", kwargs=context)

    def current_step_url(self):
        return reverse("survey-detail-step", kwargs={"id": self.survey.id, "step": self.step})

    def save(self, commit=True):
        """Save the response object"""
        response = super().save(commit=False)
        response.survey = self.survey
        response.survey_founder = self.survey.founder
        response.interview_uuid = self.uuid
        if self.user.is_authenticated:
            response.user = self.user
        response.repeat_order = self.repeat_order
        response.save()

        data = {"survey_id": response.survey.id, "interview_uuid": response.interview_uuid, "responses": []}
        for field_name, field_value in list(self.cleaned_data.items()):
            if field_name.startswith("question_"):
                # print("field_name:      ", field_name)
                field_name_split = field_name.split("_")
                # print("field_name_split:      ", field_name_split)
                if field_name_split[1] != "subsidiary":
                    q_id = int(field_name.split("_")[1])
                    question = Question.objects.get(pk=q_id)
                    answer = Answer(question=question)
                    NB = int(question.number_of_responses)
                    NB += 1
                    question.number_of_responses = NB
                    question.save()
                    answer.body = field_value
                    data["responses"].append((answer.question.id, answer.body))
                    LOGGER.debug("Creating answer for question %d of type %s : %s", q_id, answer.question.type, field_value)
                    answer.response = response
                    answer.save()

                elif field_name_split[1] == "subsidiary":
                    q_id = int(field_name.split("_")[2])
                    question = Question.objects.get(pk=q_id)
                    try:
                        answers = Answer.objects.filter(response=response, question=question).prefetch_related("question").first()
                        answers.subsidiary = field_value
                        answers.save()
                    except Answer.DoesNotExist:
                        print("Error:")

                    # 更新最多回答的记录
                    answers_all_saved = Answer.objects.filter(question=question)
                    majority_choices_list = []
                    for ans in answers_all_saved:
                        majority_choices_list.append(ans.body)
                    question.majority_choices = max(majority_choices_list, key=majority_choices_list.count)
                    question.save()

        Majority_Rate_num, Correctness_Rate_num = calculate_results(response)
        response_list = Response.objects.filter(survey=self.survey)
        if len(response_list)>1:
            for response_t in response_list:
                Majority_Rate_num, Correctness_Rate_num = calculate_results(response_t)

        print("Forms saved.     Majority_Rate_num=", Majority_Rate_num)
        print("Forms saved.  Correctness_Rate_num=", Correctness_Rate_num)

        cache.delete("step_{}_{}".format(self.user, self.survey))


        survey_completed.send(sender=Response, instance=response, data=data)
        return response
