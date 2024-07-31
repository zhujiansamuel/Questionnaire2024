from ..models.response import Response

def Diagnostic_Analyze(majority_rate, correctness_rate, kwargs):

    kwargs_step = kwargs.get("step")
    if kwargs_step is None:
        response = Response.objects.get(interview_uuid=kwargs["uuid"])
        step = int(response.number_of_questions)
    else:
        step = int(kwargs_step)+1

    print("Step:  ",step)
    majority_rate_r = majority_rate/step
    if majority_rate_r < 0.55:
        msg_1 = "D"
    elif majority_rate_r < 0.65:
        msg_1 = "C"
    elif majority_rate_r < 0.75:
        msg_1 = "B"
    elif majority_rate_r >= 0.75:
        msg_1 = "A"

    correctness_rate_r = correctness_rate/step
    if correctness_rate_r == 0:
        msg_2 = "Zero"
        msg_1 = "Zero"
    elif correctness_rate_r < 0.55:
        msg_2 = "IV"
    elif correctness_rate_r < 0.65:
        msg_2 = "III"
    elif correctness_rate_r < 0.75:
        msg_2 = "II"
    elif correctness_rate_r >= 0.75:
        msg_2 = "I"

    msg = msg_1 + "-" + msg_2
    if msg=="Zero-Zero":
        # case "Zero-Zero":
            result_msg = """
            申し訳ありませんが、まだ十分な回答が得られていません。また後で診断結果を見直してください。
            """
    elif msg == "A-I":
        # case "A-I":
            result_msg = """
            You are quite ordinary and know yourself very much. 
It is your strength that you know how other people would think. 
And this may give you a reason to try to think differently than others! 
At the same time, continue the game and you may still find unexpected aspect of yourself here.
<br>
<br>
あなたはごく普通で、自分のことをよく理解している。
他の人がどう考えるかを知っているのは、あなたの強みです。
そしてそれが、他の人とは違う考え方をしようとするきっかけになるかもしれない！
同時に、ゲームを続ければ、自分の意外な一面を発見できるかもしれない。
            """
    elif msg =="A-II":
            result_msg = """
You are quite ordinary and know yourself enough. 
And this may give you a reason to try to think differently than others! 
At the same time, continue the game and better understand yourself. You may still find unexpected aspect of yourself here. 
<br>
<br>
あなたはごく普通で、自分自身のことを十分に理解している。
そしてこのことが、他の人とは違う考え方をしようとする理由になるかもしれない！
同時に、ゲームを続け、自分自身をよりよく理解しよう。自分の意外な一面を発見できるかもしれない。
            """
    elif msg =="B-I":
            result_msg = """
You are generally ordinary and know yourself very much. 
It is your strength that you know how other people would think. 
And this may give you a reason to try to think differently than others! 
At the same time, continue the game and you may still find unexpected aspect of yourself here. 
<br>
<br>
あなたは概して平凡で、自分のことをよく理解している。
他の人がどう考えるかを知っているのは、あなたの強みだ。
そしてこのことが、他の人とは違う考え方をしようとする理由になるかもしれない！
同時に、ゲームを続ければ、自分の意外な一面を発見できるかもしれない。
            """
    elif msg == "B-II":
            result_msg = """
You are generally ordinary and know yourself enough. 
And this may give you a reason to try to think differently than others! 
At the same time, continue the game and better understand yourself. You may still find unexpected aspect of yourself here.
<br>
<br>
あなたは一般的に平凡で、自分自身を十分に理解している。
そしてこのことが、他の人とは違う考え方をしようとする理由になるかもしれない！
同時に、ゲームを続け、自分自身をよりよく理解しよう。自分の意外な一面を発見できるかもしれない。
            """
    elif msg == "A-III":
            result_msg = """
You are not so unique or unusual as you think. 
It is better for you to revise your self-image. 
Train yourself through this game, and know yourself better by learning how other people would think. 
<br>
<br>
あなたが思っているほど、あなたはユニークでも変わっているわけでもない。
自己イメージを見直した方がいい。
このゲームを通して自分を鍛え、他の人がどう考えるかを知ることで、自分をよりよく知ることができる。
            """
    elif msg == "B-III":
            result_msg = """
You are not so unique or unusual as you think. 
It is better for you to revise your self-image. 
Train yourself through this game, and know yourself better by learning how other people would think. 
<br>
<br>
あなたが思っているほど、あなたはユニークでも変わっているわけでもない。
自己イメージを見直した方がいい。
このゲームを通して自分を鍛え、他の人がどう考えるかを知ることで、自分をよりよく知ることができる。
            """
    elif msg == "A-IV":
            result_msg = """
Know yourself better! 
You are not at all unique or unusual as you think. 
It is very risky for you to have a wrong self-image. 
Train yourself through this game, and know yourself better by learning how other people would think. 
<br>
<br>
もっと自分を知ろう！
あなたが思っているほど、あなたは決してユニークでも変わっているわけでもない。
間違った自己イメージを持つことは非常に危険だ。
このゲームを通して自分を鍛え、他の人がどう考えるかを知ることで、自分をもっとよく知ろう。
            """
    elif msg == "B-IV":
            result_msg = """
Know yourself better! 
You are not at all unique or unusual as you think. 
It is very risky for you to have a wrong self-image. 
Train yourself through this game, and know yourself better by learning how other people would think. 
<br>
<br>
もっと自分を知ろう！
あなたが思っているほど、あなたは決してユニークでも変わっているわけでもない。
間違った自己イメージを持つことは非常に危険だ。
このゲームを通して自分を鍛え、他の人がどう考えるかを知ることで、自分をもっとよく知ろう。
            """
    elif msg == "C-I":
            result_msg = """
You are a little different from others and you know yourself very well. 
This is your virtue and strength. 
Congratulations!
Continue the game and you may still find unexpected aspect of yourself here. 
<br>
<br>
あなたは他の人とは少し違っていて、自分のことをよく知っている。
これはあなたの美徳であり、強みです。
おめでとう！
ゲームを続ければ、自分の意外な一面を発見できるかもしれません。
            """
    elif msg == "C-II":
            result_msg = """
You are a little different from others and you know yourself enough. 
This is your virtue and strength. 
Congratulations!
But you can still improve your understanding of yourself through this game. 
Continue the game and better understand yourself. You may still find unexpected aspect of yourself here. 
<br>
<br>
あなたは他の人とは少し違っていて、自分自身を十分に理解している。
これがあなたの美徳であり、強みなのです。
おめでとう！
でも、このゲームを通して、自分自身への理解を深めることはできます。
ゲームを続けて、もっと自分を理解してください。自分の意外な一面を発見できるかもしれません。
            """
    elif msg == "C-III":
            result_msg = """
You are a little different from others, but you seem to be unaware of yourself in relation to other people. 
You are not so ordinary or usual as you think. 
Train yourself through this game, and know yourself better by learning how other people would think.
<br>
<br>
あなたは他の人とは少し違っているが、他の人たちとの関係で自分自身に気づいていないようだ。
あなたが思っているほど、あなたは普通でもなんでもない。
このゲームを通して自分を鍛え、他の人がどう考えるかを知ることで、自分をもっとよく知ろう。
            """
    elif msg == "C-IV":
            result_msg = """
You are a little different from others, but it is very risky for you to remain ignorant of your uniqueness. 
You are not at all ordinary or usual as you think. 
Train yourself through this game, and know yourself better by learning how other people would think. 
<br>
<br>
あなたは他の人とは少し違うが、自分のユニークさに気づかないままでいるのはとても危険だ。
あなたが思っているほど、あなたは普通でもなんでもない。
このゲームを通して自分を鍛え、他の人がどう考えるかを知ることで、自分をよりよく知ることができる。
            """
    elif msg == "D-I":
            result_msg = """
It is your virtue that you are very different from others, and it is your strength that you are well aware of your uniqueness. 
Congratulations!
Continue the game and you may still find unexpected aspect of yourself here. 
<br>
<br>
他の人とは全く違うということがあなたの美徳であり、自分のユニークさをよく認識していることがあなたの強みなのです。
おめでとう！
ゲームを続ければ、自分の意外な一面を発見できるかもしれない。
            """
    elif msg == "D-II":
            result_msg = """
It is your virtue that you are very different from others, and you are generally aware of your uniqueness. 
Continue the game and better understand yourself. You may still find unexpected aspect of yourself here. 
<br>
<br>
自分が他の人とは全く違うということは、あなたの美徳であり、あなたは自分のユニークさを一般的に自覚している。
ゲームを続けて、自分自身をもっと理解してください。自分の意外な一面を発見できるかもしれない。
            """
    elif msg == "D-III":
            result_msg = """
It is your virtue that you are very different from others. However, you seem to be unaware of your uniqueness. 
You are not so ordinary or usual as you think. 
Train yourself through this game, and know yourself better by learning how other people would think. 
<br>
<br>
自分が他人と大きく異なるのは、あなたの美徳だ。しかし、あなたは自分のユニークさに気づいていないようだ。
あなたが思っているほど、あなたは普通でもなんでもない。
このゲームを通して自分を鍛え、他の人がどう考えるかを学ぶことで、自分をよりよく知ることができる。
            """
    elif msg == "D-IV":
            result_msg = """
Know yourself better! You are not at all ordinary or usual as you think. 
It is your virtue that you are very different from others. However, it is very risky for you to remain ignorant of your uniqueness. 
Train yourself through this game, and know yourself better by learning how other people would think. 
<br>
<br>
もっと自分を知ろう！あなたが思っているほど、あなたは普通でもなんでもない。
他の人とは全く違うのがあなたの美徳なのです。しかし、自分のユニークさに気づかないままでいることは非常に危険だ。
このゲームを通して自分を鍛え、他の人がどう考えるかを学ぶことで、自分をもっとよく知ろう。
            """

    return msg, result_msg, majority_rate_r, correctness_rate_r

