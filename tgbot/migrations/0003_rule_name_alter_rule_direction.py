# Generated by Django 4.2.3 on 2023-12-22 02:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tgbot", "0002_folder_rule_forwarding_filter"),
    ]

    operations = [
        migrations.AddField(
            model_name="rule",
            name="name",
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name="rule",
            name="direction",
            field=models.CharField(
                choices=[("O", "One-way"), ("X", "Two-way")],
                default=("O", "One-way"),
                max_length=1,
            ),
        ),
    ]
