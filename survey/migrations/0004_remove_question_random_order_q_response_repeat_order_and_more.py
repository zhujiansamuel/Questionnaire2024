# Generated by Django 4.2.10 on 2024-02-29 06:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("survey", "0003_remove_category_random_order"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="question",
            name="random_order_q",
        ),
        migrations.AddField(
            model_name="response",
            name="repeat_order",
            field=models.IntegerField(default=0, verbose_name="repeat_order"),
        ),
        migrations.AlterField(
            model_name="answer",
            name="subsidiary",
            field=models.CharField(
                choices=[("majority", "多数派"), ("minority", "少数派")],
                default="majority",
                max_length=9,
                verbose_name="前の質問で、あなたが答えた回答は多数派だと想いますか、少数派だと思いますか？",
            ),
        ),
        migrations.AlterField(
            model_name="category",
            name="block_type",
            field=models.CharField(
                choices=[("sequence", "sequence"), ("one-random", "one-random")],
                default="sequence",
                help_text="\n\n",
                max_length=200,
                verbose_name="block type",
            ),
        ),
    ]
