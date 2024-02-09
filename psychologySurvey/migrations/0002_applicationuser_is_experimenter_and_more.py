# Generated by Django 4.1 on 2024-02-09 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("psychologySurvey", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="applicationuser",
            name="is_experimenter",
            field=models.BooleanField(
                default=False,
                help_text="By default, the added user does not have experimenter privileges. If you need to create an experimenter with administrative rights, select it here.",
                verbose_name="Experimenter",
            ),
        ),
        migrations.AddField(
            model_name="applicationuser",
            name="is_participant",
            field=models.BooleanField(
                default=True,
                help_text="Newly created users are eligible to participate in the experiment by default.",
                verbose_name="Participant",
            ),
        ),
        migrations.AlterField(
            model_name="applicationuser",
            name="Gender",
            field=models.CharField(
                choices=[("Female", "Gemale"), ("Other", "Other"), ("Male", "Male")],
                default="Other",
                help_text="Non-essential items. Please rely on the experimenter's prompts to determine if an answer is required.",
                max_length=10,
                verbose_name="Gender",
            ),
        ),
        migrations.AlterField(
            model_name="applicationuser",
            name="email",
            field=models.EmailField(
                max_length=254, unique=True, verbose_name="E-mail address"
            ),
        ),
    ]
