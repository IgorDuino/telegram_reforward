# Generated by Django 4.2.8 on 2024-01-29 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0012_alter_filtertriggertemplate_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='rule',
            name='allow_a_chat_members_control',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='rule',
            name='allow_b_chat_members_control',
            field=models.BooleanField(default=False),
        ),
    ]
