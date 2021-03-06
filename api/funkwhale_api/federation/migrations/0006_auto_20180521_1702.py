# Generated by Django 2.0.4 on 2018-05-21 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("federation", "0005_auto_20180413_1723")]

    operations = [
        migrations.AlterField(
            model_name="library", name="url", field=models.URLField(max_length=500)
        ),
        migrations.AlterField(
            model_name="librarytrack",
            name="audio_url",
            field=models.URLField(max_length=500),
        ),
        migrations.AlterField(
            model_name="librarytrack",
            name="url",
            field=models.URLField(max_length=500, unique=True),
        ),
    ]
