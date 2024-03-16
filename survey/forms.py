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

from survey.models import Answer, Category, Question, Response, Survey
from survey.signals import survey_completed
from survey.widgets import ImageSelectWidget

LOGGER = logging.getLogger(__name__)

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
        self.survey = kwargs.pop("survey")
        self.user = kwargs.pop("user")
        self.requests = kwargs.pop("requests")
        #
        try:
            self.step = int(kwargs.pop("step"))
        except KeyError:
            self.step = None
        super().__init__(*args, **kwargs)
        self.uuid = uuid.uuid4().hex

        self.response = False
        self.answers = False
        self.preexisting_response = self._get_preexisting_response()

        # 以下内容用于实现产生新的response
        # -------------------------------------------------------------------
        # -------------------------------------------------------------------
        # -------------------------------------------------------------------
        # -------------------------------------------------------------------

        if self.response and self.response.count() > 1:
            repeat_order_list = [int(response_temp.repeat_order) for response_temp in self.response]
            # todo 根据情况决定是否需要添加完成状态判断
            # repeat_order_list = [int(response_temp.repeat_order) for response_temp in self.response if response_temp.completion_status=="Completed"]
            self.repeat_order = max(repeat_order_list) + 1
            self.response = None
        elif self.response and self.response.count() == 1:
            self.repeat_order = self.response.repeat_order + 1
            self.response = None
        else:
            self.repeat_order = 0
        if settings.DISPLAY_SURVEY_QUESTIONNAIRE_INFORMATION:
            print(" ---------------------after----------------------------- ")
            print("self.preexisting_response:    ",self.preexisting_response)
            print("self.repeat_order:   ",self.repeat_order)
            print("self.response:  ",self.response)
            print(" ------------------------------------------------------------ ")



            # print(" ----------------------已经回答的问题-------------------------- ")
            # if self.preexisting_response.count() > 1:
            #     for response_temp in self.preexisting_response:
            #         questions = Question.objects.filter(survey=response_temp.survey).prefetch_related("answers")
            #         questions_a = [q for q in questions if q.answers is None]
            #         print("-->> questions_a",questions_a)
                # for question in questions_a:
                #     print("----> question:    ",question)
                #     print("------> question.answers:    ", question.answers)
                #     print("---------> question.answers.IS:    ", question.answers is None)

                # print("response_temp.survey.questions",response_temp.survey.questions)

        # -------------------------------------------------------------------
        # -------------------------------------------------------------------
        # -------------------------------------------------------------------
        # -------------------------------------------------------------------
        # TranslateComments
        # 以下的内容设定了每个调查问卷中的问题设置
        # -------------------------------------------------------------------
        # -------------------------------------------------------------------
        # -------------------------------------------------------------------
        # -------------------------------------------------------------------
        # TranslateComments
        # 初始化会话随机列表
        session_random_list = self.requests.session.get("session_random_list", False)
        # # TranslateComments
        # # 初始化问卷调查诊断
        # diagnostic_session_key = "diagnostic_{}_{}".format(self.requests.user,self.survey.name)
        # if diagnostic_session_key in self.requests.session:
        #     self.requests.session[diagnostic_session_key]={}
        #     self.requests.session[diagnostic_session_key]["Majority_Rate"] = "0"
        #     self.requests.session[diagnostic_session_key]["Correctness_Rate"] = "0"

        # if not session_random_list:
        #     self.request.session["session_random_list"] = {}
        #     for i in range(1, 100):
        #         self.request.session["session_random_list"][str(i)] = random.randint(100, 9999999)

        # TranslateComments
        # 此方法返回由order与id排序的分类
        # self.categories = self.survey.non_empty_categories()
        # TranslateComments
        # 此方法返回由order与random_order排序的伪随机的分类
        # self.categories = self.survey.random_categories()

        categories_s = self.survey.random_categories()
        categories_dic = {}
        for i,category in enumerate(categories_s):
            random_order = session_random_list[str(i+1)]
            categories_dic[random_order] = category
        categories_dic_sorted = sorted(categories_dic.items(), key=lambda x:x[0] )
        self.categories = [v for i,v in categories_dic_sorted]

        self.qs_with_no_cat = self.survey.questions.filter(category__isnull=True).order_by("order", "id")

        # TranslateComments
        # 获取隐藏问题，它们将被安插进允许由隐藏问题的类别中
        self.hiding_question_category = [x for x in list(self.survey.categories.order_by("id")) if x.name == "hiding_question"]
        if self.hiding_question_category:
            self.hiding_question = list(self.hiding_question_category[0].questions.order_by("-hiding_question_category_order"))
        else:
            self.hiding_question = []

        # TranslateComments
        # self.question_to_display是可以显示在调查问卷中的问题的list
        self.question_to_display = []
        for i_category,category in enumerate(self.categories):
            if category.block_type == "sequence":
                # TranslateComments
                # 对于1类类别，可加入隐藏问题
                # 隐藏类别的问题并不会独立显示而是根据category.hiding_question_order决定放在该类别的那个位置
                # 隐藏问题在第几个block中显示由question.hiding_question_category_order设定
                if category.display_num <= len(category.questions.all()):
                    # TranslateComments
                    # 如果设置的显示数量小于或者等于问题数目，那么按照设定的显示数量显示问题
                    question_s = category.questions.all()[:int(category.display_num)]
                elif category.display_num>len(category.questions.all()):
                    # TranslateComments
                    # 如果设置的显示数量大于问题数目，那么显示全部的问题，忽略设定的显示数量
                    question_s = category.questions.all()
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
                                    question_add += hq

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
                all_question = category.questions.all()
                random_question_dic = {}
                for i, question in enumerate(all_question):
                    random_order = session_random_list[str(i + 10)]
                    random_question_dic[random_order] = question
                random_question_dic_sorted = sorted(random_question_dic.items(), key=lambda x: x[0])
                random_question = [v for i, v in random_question_dic_sorted][0]

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

        # -------------------------------------------------------------------
        if settings.DISPLAY_SURVEY_QUESTIONNAIRE_INFORMATION:
            print(" ------------------------------------------------------------ ")
            print("生成的问题")
            print(" -------- ")
            for i, question in enumerate(self.question_to_display):
                print("生成的问题  ", str(i), " :", question.text, "    ", question.category.name)
            print(" ------------------------------------------------------------ ")
        # -------------------------------------------------------------------
        # TranslateComments

        if self.survey.display_method == Survey.BY_CATEGORY:
            self.steps_count = len(self.categories) + (1 if self.qs_with_no_cat else 0)
        else:
            self.steps_count = len(self.question_to_display)
        # -------------------------------------------------------------------
        # -------------------------------------------------------------------
        # -------------------------------------------------------------------
        # -------------------------------------------------------------------
        # -------------------------------------------------------------------
        # -------------------------------------------------------------------
        # -------------------------------------------------------------------

        self.add_questions(kwargs.get("data"))

        # 不需要看到已经回答的问题
        # self._get_preexisting_response()
        # if not self.survey.editable_answers and self.response is not None:
        #     for name in self.fields.keys():
        #         self.fields[name].widget.attrs["disabled"] = True

    def add_questions(self, data):
        # add a field for each survey question, corresponding to the question
        # type as appropriate.
        # -------------------------------------------------------------------
        if self.survey.display_method == Survey.BY_CATEGORY and self.step is not None:
            pass
            # if self.step == len(self.categories):
            #     qs_for_step = self.survey.questions.filter(category__isnull=True).order_by("order", "id")
            # else:
            #     qs_for_step = self.survey.questions.filter(category=self.categories[self.step]) # 分类的顺序即self.categories序列的顺序
            #                                                                                     # 所以是不是只要改变self.categories序列的顺序就可以实现类别随机化
            # # 获取一定数量的问题
            # for question in qs_for_step:
            #     self.add_question(question, data)
        else:
            for i, question in enumerate(self.question_to_display):
                not_to_keep = i != self.step and self.step is not None
                if self.survey.display_method == Survey.BY_QUESTION and not_to_keep:
                    continue
                self.add_question(question, data)

    def current_categories(self):
        if self.survey.display_method == Survey.BY_CATEGORY:
            pass
            # if self.step is not None and self.step < len(self.categories):
            #     return [self.categories[self.step]]
            # return [Category(name="No category", description="No cat desc")]
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
        # sam-todo 既有答案中的meta选项的选取
        # 由于需要实现回答过的问题不在显示，所以需要重写这个方法
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
        # sam-todo 既有答案中的meta选项的选取
        # 由于需要实现回答过的问题不在显示，所以需要重写这个方法
        """Recover a pre-existing answer in database.

        The user must be logged. A Response containing the Answer must exists.

        :param Question question: The question we want to recover in the
        response.
        :rtype: Answer or None"""
        answers = self._get_preexisting_answers()
        return answers.get(question.id, None)

    def get_question_initial(self, question, data):
        """Get the initial value that we should use in the Form

        :param Question question: The question
        :param dict data: Value from a POST request.
        :rtype: String or None"""
        initial = None
        # ------------------------
        # answer = self._get_preexisting_answer(question)
        # if answer:
        #     # Initialize the field with values from the database if any
        #     if question.type == Question.SELECT_MULTIPLE:
        #         initial = []
        #         if answer.body == "[]":
        #             pass
        #         elif "[" in answer.body and "]" in answer.body:
        #             initial = []
        #             unformated_choices = answer.body[1:-1].strip()
        #             for unformated_choice in unformated_choices.split(settings.CHOICES_SEPARATOR):
        #                 choice = unformated_choice.split("'")[1]
        #                 initial.append(slugify(choice))
        #         else:
        #             # Only one element
        #             initial.append(slugify(answer.body))
        #     else:
        #         initial = answer.body
        # ------------------------
        if data:
            # Initialize the field field from a POST request, if any.
            # Replace values from the database
            initial = data.get("question_%d" % question.pk)
        return initial

    def get_question_widget(self, question):
        """Return the widget we should use for a question.

        :param Question question: The question
        :rtype: django.forms.widget or None"""
        try:
            return self.WIDGETS[question.type]
        except KeyError:
            return None

    @staticmethod
    def get_question_choices(question):
        """Return the choices we should use for a question.

        :param Question question: The question
        :rtype: List of String or None"""
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
        """Add a question to the form.
        :param Question question: The question to add.
        :param dict data: The pre-existing values from a post request."""
        kwargs = {"label": question.text, "required": question.required, "help_text": question.subsidiary_type}

        # initial = self.get_question_initial(question, data)
        # if initial:
        #     kwargs["initial"] = initial

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
            context = {"id": self.survey.id, "step": self.step + 1}
            return reverse("survey-detail-step", kwargs=context)

    def current_step_url(self):
        return reverse("survey-detail-step", kwargs={"id": self.survey.id, "step": self.step})

    # def get_current_question_subsidiary_type(self):
    #     return

    def save(self, commit=True):
        """Save the response object"""
        # Recover an existing response from the database if any
        #  There is only one response by logged user.
        # response = self._get_preexisting_response()
        # if not self.survey.editable_answers and response is not None:
        #     return None
        # if response is None:
        response = super().save(commit=False)

        response.survey = self.survey
        response.interview_uuid = self.uuid
        if self.user.is_authenticated:
            response.user = self.user
        response.repeat_order = self.repeat_order

        response.save()
        data = {"survey_id": response.survey.id, "interview_uuid": response.interview_uuid, "responses": []}
        for field_name, field_value in list(self.cleaned_data.items()):
            if field_name.startswith("question_"):
                field_name_split = field_name.split("_")
                if field_name_split[1] != "subsidiary":
                    q_id = int(field_name.split("_")[1])
                    question = Question.objects.get(pk=q_id)

                    # answer = self._get_preexisting_answer(question)
                    # if answer is None:
                    answer = Answer(question=question)

                    # if question.type == Question.SELECT_IMAGE:
                    #     value, img_src = field_value.split(":", 1)
                    #     LOGGER.debug("Question.SELECT_IMAGE not implemented, please use : %s and %s", value, img_src)

                    answer.body = field_value
                    data["responses"].append((answer.question.id, answer.body))
                    LOGGER.debug("Creating answer for question %d of type %s : %s", q_id, answer.question.type, field_value)
                    answer.response = response
                    answer.save()

                elif field_name_split[1] == "subsidiary":
                    q_id = int(field_name.split("_")[2])
                    question = Question.objects.get(pk=q_id)

                    # answer = self._get_preexisting_answer(question)
                    # if answer is None:
                    # answer = Answer(question=question)
                    try:
                        answers = Answer.objects.filter(response=response).prefetch_related("question")
                        answers_dict = {answer.question.id: answer for answer in answers.all()}
                    except Answer.DoesNotExist:
                        print("Error:")

                    if settings.DISPLAY_SURVEY_QUESTIONNAIRE_INFORMATION:
                        print(" ------------------------------------------------------------ ")
                        print("answers:   ", answers)
                        print("q_id:  ", q_id)
                        print(" ------------------------------------------------------------ ")


                    answer = answers_dict[str(q_id)]

                    # if question.type == Question.SELECT_IMAGE:
                    #     value, img_src = field_value.split(":", 1)
                    #     LOGGER.debug("Question.SELECT_IMAGE not implemented, please use : %s and %s", value, img_src)
                    answer.subsidiary = field_value
                    answer.save()
                    # data["responses"].append((answer.question.id, answer.body))
                    # data["responses"].append((answer.question_id,answer.subsidiary))
                    # LOGGER.debug("Creating answer for question %d of type %s : %s", q_id, answer.question.type,
                    #              field_value)
                    # answer.response = response
                    # answer.save()
        survey_completed.send(sender=Response, instance=response, data=data)
        return response
