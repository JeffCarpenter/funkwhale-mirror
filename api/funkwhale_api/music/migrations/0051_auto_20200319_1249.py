# Generated by Django 3.0.4 on 2020-03-19 12:49

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0050_auto_20200129_1344'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='album',
            name='cover',
        ),
        migrations.AddField(
            model_name='artist',
            name='modification_date',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='upload',
            name='import_status',
            field=models.CharField(choices=[('draft', 'Draft'), ('pending', 'Pending'), ('finished', 'Finished'), ('errored', 'Errored'), ('skipped', 'Skipped')], default='pending', max_length=25),
        ),
        migrations.AlterField(
            model_name='uploadversion',
            name='mimetype',
            field=models.CharField(choices=[('audio/mpeg3', 'mp3'), ('audio/x-mp3', 'mp3'), ('audio/mpeg', 'mp3'), ('video/ogg', 'ogg'), ('audio/ogg', 'ogg'), ('audio/opus', 'opus'), ('audio/x-m4a', 'aac'), ('audio/x-m4a', 'm4a'), ('audio/x-flac', 'flac'), ('audio/flac', 'flac')], max_length=50),
        ),
    ]
