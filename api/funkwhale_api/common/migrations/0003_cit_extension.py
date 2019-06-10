# Generated by Django 2.0.2 on 2018-02-27 18:43
from django.db import migrations
from django.contrib.postgres.operations import CITextExtension


class CustomCITExtension(CITextExtension):
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        check_sql = "SELECT 1 FROM pg_extension WHERE extname = 'citext'"
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(check_sql)
            result = cursor.fetchall()

        if result:
            return
        return super().database_forwards(app_label, schema_editor, from_state, to_state)


class Migration(migrations.Migration):

    dependencies = [("common", "0002_mutation")]

    operations = [CustomCITExtension()]