# Generated by Django 2.2.16 on 2022-04-11 23:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("publications", "0002_auto_20220411_1234"),
    ]

    operations = [
        migrations.RenameField(
            model_name="compaspublication",
            old_name="dataset_DOI",
            new_name="dataset_doi",
        ),
        migrations.RenameField(
            model_name="compaspublication",
            old_name="journal_DOI",
            new_name="journal_doi",
        ),
    ]
