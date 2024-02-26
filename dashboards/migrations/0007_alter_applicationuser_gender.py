# Generated by Django 4.1 on 2024-02-17 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboards", "0006_alter_applicationuser_gender"),
    ]

    operations = [
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
    ]