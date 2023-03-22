# Generated by Django 3.2.13 on 2023-03-22 06:28

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('compasui', '0016_auto_20221122_0437'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileDownloadToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.UUIDField(db_index=True, default=uuid.uuid4, unique=True)),
                ('path', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='compasui.compasjob')),
            ],
        ),
    ]
