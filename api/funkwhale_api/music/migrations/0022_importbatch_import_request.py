# Generated by Django 2.0.2 on 2018-02-20 22:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('requests', '__first__'),
        ('music', '0021_populate_batch_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='importbatch',
            name='import_request',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='import_batches', to='requests.ImportRequest'),
        ),
    ]