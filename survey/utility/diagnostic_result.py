
def Diagnostic_Result(majority_rate, correctness_rate, number_of_questions):
    step = int(number_of_questions)
    majority_rate = int(majority_rate)
    correctness_rate = int(correctness_rate)
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
            Sorry,we don't haven enough answers yet.
            """
    elif msg == "A-I":
        # case "A-I":
            result_msg = """
            You are quite ordinary and know yourself very much. 
It is your strength that you know how other people would think. 
And this may give you a reason to try to think differently than others! 
At the same time, continue the game and you may still find unexpected aspect of yourself here.
<br>
あなたはごく平凡で、自分のことを大変よく理解しています。
他人がどう考えるかを知っているのは、あなたの強みです。 
そしてこれは、あなたが他の人とは違う考え方をする理由を与えてくれるかもしれません！ 
それでも、このゲームを続けることで、自分の意外な一面を見つけることができるかもしれません。

            """
    elif msg =="A-II":
            result_msg = """
You are quite ordinary and know yourself enough. 
And this may give you a reason to try to think differently than others! 
At the same time, continue the game and better understand yourself. You may still find unexpected aspect of yourself here. 
<br>
あなたはごく平凡で、自分のことを十分理解しています。 
そしてこれは、あなたが他の人とは違う考え方をする理由を与えてくれるかもしれません！
同時に、このゲームを続けることで、自分についてさらによく理解し、自分の意外な一面を見つけることができるかもしれません。
。
            """
    elif msg =="B-I":
            result_msg = """
You are generally ordinary and know yourself very much. 
It is your strength that you know how other people would think. 
And this may give you a reason to try to think differently than others! 
At the same time, continue the game and you may still find unexpected aspect of yourself here. 
<br>
あなたは概して普通の人で、自分のことを大変よく理解しています。
他人がどう考えるかを知っているのは、あなたの強みです。
そしてこれは、あなたが他の人とは違う考え方をする理由を与えてくれるかもしれません！
それでも、このゲームを続けることで、自分の意外な一面を見つけることができるかもしれません。

            """
    elif msg == "B-II":
            result_msg = """
You are generally ordinary and know yourself enough. 
And this may give you a reason to try to think differently than others! 
At the same time, continue the game and better understand yourself. You may still find unexpected aspect of yourself here.
<br>
あなたは概して普通の人で、自分のことを十分理解しています。 
そしてこれは、あなたが他の人とは違う考え方をする理由を与えてくれるかもしれません！
それでも、このゲームを続けることで、自分についてさらによく理解し、自分の意外な一面を見つけることができるかもしれません。

            """
    elif msg == "A-III":
            result_msg = """
You are not so unique or unusual as you think. 
It is better for you to revise your self-image. 
Train yourself through this game, and know yourself better by learning how other people would think. 
<br>
あなたが思っているほど、あなたはユニークでも珍しい存在でもありません。 
自己イメージを見直した方がいいかもしれません。
このゲームを通じて訓練し、他の人がどう考えるかを学ぶことで、自分をよりよく知るようになりましょう。

            """
    elif msg == "B-III":
            result_msg = """
You are not so unique or unusual as you think. 
It is better for you to revise your self-image. 
Train yourself through this game, and know yourself better by learning how other people would think. 
<br>
あなたが思っているほど、あなたはユニークでも珍しい存在でもありません。 
自己イメージを見直した方がいいかもしれません。
このゲームを通じて訓練し、他の人がどう考えるかを学ぶことで、自分をよりよく知るようになりましょう。

            """
    elif msg == "A-IV":
            result_msg = """
Know yourself better! 
You are not at all unique or unusual as you think. 
It is very risky for you to have a wrong self-image. 
Train yourself through this game, and know yourself better by learning how other people would think. 
<br>
もっと自分を知りましょう！ 
あなたが思っているほど、あなたは全くユニークでも珍しい存在でもありません。 
間違った自己イメージを持つことは非常に危険です。 
このゲームを通じて訓練し、他の人がどう考えるかを学ぶことで、自分をよりよく知るようになりましょう。

            """
    elif msg == "B-IV":
            result_msg = """
Know yourself better! 
You are not at all unique or unusual as you think. 
It is very risky for you to have a wrong self-image. 
Train yourself through this game, and know yourself better by learning how other people would think. 
<br>
もっと自分を知りましょう！ 
あなたが思っているほど、あなたは全くユニークでも珍しい存在でもありません。 
間違った自己イメージを持つことは非常に危険です。 
このゲームを通じて訓練し、他の人がどう考えるかを学ぶことで、自分をよりよく知るようになりましょう。

            """
    elif msg == "C-I":
            result_msg = """
You are a little different from others and you know yourself very well. 
This is your virtue and strength. 
Congratulations!
Continue the game and you may still find unexpected aspect of yourself here. 
<br>
あなたは他の人とは少し違っていて、自分のことを大変よく理解しています。
これはあなたの美徳であり、強さです。 
おめでとうございます！
それでも、このゲームを続けることで、自分の意外な一面を見つけることができるかもしれません。

            """
    elif msg == "C-II":
            result_msg = """
You are a little different from others and you know yourself enough. 
This is your virtue and strength. 
Congratulations!
But you can still improve your understanding of yourself through this game. 
Continue the game and better understand yourself. You may still find unexpected aspect of yourself here. 
<br>
あなたは他の人とは少し違っていて、自分のことを十分理解しています。
これはあなたの美徳であり、強さです。 
おめでとうございます！
それでも、このゲームを通じて自分自身への理解をさらに深めることができます。 
このゲームを続けることで、自分自身の意外な一面を、まだここで見つけることができるかもしれません。 

            """
    elif msg == "C-III":
            result_msg = """
You are a little different from others, but you seem to be unaware of yourself in relation to other people. 
You are not so ordinary or usual as you think. 
Train yourself through this game, and know yourself better by learning how other people would think.
<br>
あなたは他の人とは少し違っていますが、他の人と比べた自分自身に気づいていないようです。
あなたは自分で思っているほど平凡でも普通でもありません。
このゲームを通じて訓練し、他の人がどう考えるかを学ぶことで、自分をよりよく知るようになりましょう。

            """
    elif msg == "C-IV":
            result_msg = """
You are a little different from others, but it is very risky for you to remain ignorant of your uniqueness. 
You are not at all ordinary or usual as you think. 
Train yourself through this game, and know yourself better by learning how other people would think. 
<br>
あなたは他の人とは少し違っていますが、自分のユニークさに気づかないままでいるのは非常に危険です。
あなたは自分が平凡で普通だと思っていますが、全くそうではありません。
このゲームを通じて訓練し、他の人がどう考えるかを学ぶことで、自分をよりよく知るようになりましょう。

            """
    elif msg == "D-I":
            result_msg = """
It is your virtue that you are very different from others, and it is your strength that you are well aware of your uniqueness. 
Congratulations!
Continue the game and you may still find unexpected aspect of yourself here. 
<br>
あなたが他の人とは大きく異なる考え方をすることは美徳であり、自分のユニークさをよく自覚していることはあなたの強みです。 
おめでとうございます！
それでも、このゲームを続けることで、自分の意外な一面を見つけることができるかもしれません。

            """
    elif msg == "D-II":
            result_msg = """
It is your virtue that you are very different from others, and you are generally aware of your uniqueness. 
Continue the game and better understand yourself. You may still find unexpected aspect of yourself here. 
<br>
あなたが他の人とは大きく異なる考え方をすることは美徳であり、あなたは自分のユニークさを自覚しています。
それでも、このゲームを続けることで、自分についてさらによく理解し、自分の意外な一面を見つけることができるかもしれません。

            """
    elif msg == "D-III":
            result_msg = """
It is your virtue that you are very different from others. However, you seem to be unaware of your uniqueness. 
You are not so ordinary or usual as you think. 
Train yourself through this game, and know yourself better by learning how other people would think. 
<br>
あなたが他の人とは大きく異なる考え方をすることは美徳です。しかし、あなたは自分のユニークさに気づいていないようです。 
あなたは自分で思っているほど平凡でも普通でもありません。
このゲームを通じて訓練し、他の人がどう考えるかを学ぶことで、自分をよりよく知るようになりましょう。
。
            """
    elif msg == "D-IV":
            result_msg = """
Know yourself better! You are not at all ordinary or usual as you think. 
It is your virtue that you are very different from others. However, it is very risky for you to remain ignorant of your uniqueness. 
Train yourself through this game, and know yourself better by learning how other people would think. 
<br>
もっと自分を知りましょう！ 
あなたは自分が平凡で普通だと思っていますが、全くそうではありません。
あなたが他の人とは大きく異なる考え方をすることは美徳です。しかし、自分のユニークさに気づかないままでいるのは非常に危険です。
このゲームを通じて訓練し、他の人がどう考えるかを学ぶことで、自分をよりよく知るようになりましょう。 

            """

    return msg, result_msg