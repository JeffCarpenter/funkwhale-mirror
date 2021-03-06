# Generated by Django 2.0.8 on 2018-09-14 20:07

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('federation', '0011_auto_20180910_1902'),
        ('music', '0030_auto_20180825_1411'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='fid',
            field=models.URLField(db_index=True, max_length=500, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='album',
            name='from_activity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='federation.Activity'),
        ),
        migrations.AddField(
            model_name='artist',
            name='fid',
            field=models.URLField(db_index=True, max_length=500, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='artist',
            name='from_activity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='federation.Activity'),
        ),
        migrations.AddField(
            model_name='track',
            name='fid',
            field=models.URLField(db_index=True, max_length=500, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='track',
            name='from_activity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='federation.Activity'),
        ),
        migrations.AddField(
            model_name='trackfile',
            name='from_activity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='federation.Activity'),
        ),
        migrations.AddField(
            model_name='work',
            name='fid',
            field=models.URLField(db_index=True, max_length=500, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='work',
            name='from_activity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='federation.Activity'),
        ),
        migrations.AlterField(
            model_name='trackfile',
            name='modification_date',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True),
        ),
    ]
