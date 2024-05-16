from ..models.answer import Answer
from ..models.question import Question
from ..models.response import Response
from ..models.survey import Survey
from ..utility.diagnostic_result import Diagnostic_Result

def calculate_results(response):
    survey = response.survey
    answers = Answer.objects.filter(response=response)
    Majority_Rate = 0
    Correctness_Rate = 0
    if len(answers) == 0:
        pass
    elif len(answers) == 1:
        if answers[0].subsidiary == "majority":
            Majority_Rate = Majority_Rate + 1
            if answers[0].body == answers[0].question.majority_choices:
                Correctness_Rate = Correctness_Rate + 1
        elif answers[0].subsidiary == "minority":
            if answers[0].body != answers[0].question.majority_choices:
                Correctness_Rate = Correctness_Rate + 1
    else:
        for answer in answers:
            question = answer.question
            if answer.subsidiary == "majority":
                Majority_Rate = Majority_Rate + 1
                if answer.body == question.majority_choices:
                    Correctness_Rate = Correctness_Rate + 1
            elif answer.subsidiary == "minority":
                if answer.body != answer.question.majority_choices:
                    Correctness_Rate = Correctness_Rate + 1
    if len(answers) != 0:
        Majority_Rate_num = Majority_Rate / len(answers)
        Correctness_Rate_num = Correctness_Rate / len(answers)
    else:
        Majority_Rate_num = 0
        Correctness_Rate_num = 0
    response.correctness_rate = Correctness_Rate
    response.Majority_Rate = Majority_Rate
    response.number_of_questions = len(answers)
    response.Majority_Rate_num = Majority_Rate_num
    response.Correctness_Rate_num = Correctness_Rate_num
    response.DIAGNOSTIC_RESULT, _ = Diagnostic_Result(Majority_Rate, Correctness_Rate,len(answers))
    response.save()
    return Majority_Rate_num, Correctness_Rate_num