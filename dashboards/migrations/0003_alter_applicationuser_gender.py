# Generated by Django 4.2.10 on 2024-02-28 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboards", "0002_alter_applicationuser_gender"),
    ]

    operations = [
        migrations.AlterField(
            model_name="applicationuser",
            name="Gender",
            field=models.CharField(
                choices=[("Other", "Other"), ("Male", "Male"), ("Female", "Gemale")],
                default="Other",
                help_text="Non-essential items. Please rely on the experimenter's prompts to determine if an answer is required.",
                max_length=10,
                verbose_name="Gender",
            ),
        ),
    ]
