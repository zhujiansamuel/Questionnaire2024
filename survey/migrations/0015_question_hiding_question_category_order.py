# Generated by Django 4.2.10 on 2024-02-26 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("survey", "0014_category_hiding_question_order_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="hiding_question_category_order",
            field=models.IntegerField(default=0, verbose_name=""),
        ),
    ]