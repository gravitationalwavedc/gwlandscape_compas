# Generated by Django 3.2.13 on 2023-04-21 05:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("publications", "0006_auto_20230206_0015"),
    ]

    operations = [
        migrations.AlterField(
            model_name="compasmodel",
            name="name",
            field=models.CharField(default="", max_length=50),
        ),
    ]
