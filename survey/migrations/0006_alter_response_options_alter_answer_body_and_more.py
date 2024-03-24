# Generated by Django 4.1 on 2024-03-23 04:58

from django.db import migrations, models
import survey.models.question


class Migration(migrations.Migration):

    dependencies = [
        ("survey", "0005_response_completion_status"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="response",
            options={
                "verbose_name": "Set of answers",
                "verbose_name_plural": "Sets of answers",
            },
        ),
        migrations.AlterField(
            model_name="answer",
            name="body",
            field=models.TextField(blank=True, null=True, verbose_name="Select"),
        ),
        migrations.AlterField(
            model_name="answer",
            name="subsidiary",
            field=models.CharField(
                choices=[("minority", "少数派"), ("majority", "多数派")],
                default="majority",
                max_length=9,
                verbose_name="Majority vs. Minority",
            ),
        ),
        migrations.AlterField(
            model_name="question",
            name="order",
            field=models.IntegerField(
                default=survey.models.question.random_number,
                help_text="\n\n",
                verbose_name="Order",
            ),
        ),
        migrations.AlterField(
            model_name="response",
            name="interview_uuid",
            field=models.CharField(max_length=36, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="response",
            name="repeat_order",
            field=models.IntegerField(default=0, verbose_name="Order of repeated"),
        ),
    ]