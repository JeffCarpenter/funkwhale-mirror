# Generated by Django 2.2.9 on 2020-01-23 13:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0007_auto_20200116_1610'),
        ('federation', '0023_actor_summary_obj'),
    ]

    operations = [
        migrations.AddField(
            model_name='actor',
            name='attachment_icon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='iconed_actor', to='common.Attachment'),
        ),
    ]