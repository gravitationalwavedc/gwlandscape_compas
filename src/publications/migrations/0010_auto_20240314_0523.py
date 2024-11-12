# Generated by Django 3.2.13 on 2024-03-14 05:23

from django.db import migrations, models
import publications.models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0009_filedownloadtoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compasdatasetmodel',
            name='file',
            field=models.FileField(blank=True, max_length=255, null=True, upload_to=publications.models.job_directory_path),
        ),
        migrations.AlterField(
            model_name='upload',
            name='file',
            field=models.FileField(blank=True, max_length=255, null=True, upload_to=''),
        ),
    ]