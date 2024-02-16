# Generated by Django 4.1 on 2024-02-14 13:41

from django.db import migrations, models
import survey.models.category


class Migration(migrations.Migration):

    dependencies = [
        ("survey", "0003_category_random_order_alter_answer_subsidiary"),
    ]

    operations = [
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
            name="random_order",
            field=models.IntegerField(
                default=survey.models.category.random_number,
                verbose_name="random order",
            ),
        ),
    ]