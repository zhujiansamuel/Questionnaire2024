# Generated by Django 4.2.10 on 2024-02-26 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("survey", "0013_alter_category_display_num"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="hiding_question_order",
            field=models.CharField(
                blank=True,
                default="1|2",
                max_length=6,
                null=True,
                verbose_name="This determines whether the hidden question is displayed in the category (0) or where within the category of questions it is displayed.",
            ),
        ),
        migrations.AlterField(
            model_name="answer",
            name="subsidiary",
            field=models.CharField(
                choices=[("minority", "少数派"), ("majority", "多数派")],
                default="majority",
                max_length=9,
                verbose_name="前の質問で、あなたが答えた回答は多数派だと想いますか、少数派だと思いますか？",
            ),
        ),
        migrations.AlterField(
            model_name="category",
            name="display_num",
            field=models.IntegerField(
                blank=True, default=10, verbose_name="Number of questions displayed"
            ),
        ),
    ]