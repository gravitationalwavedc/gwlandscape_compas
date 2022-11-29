# Generated by Django 3.2.13 on 2022-11-29 21:50

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('compasui', '0016_auto_20221122_0437'),
    ]

    operations = [
        migrations.AddField(
            model_name='singlebinaryjob',
            name='bse_grid_content',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='singlebinaryjob',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='singlebinaryjob',
            name='job_controller_id',
            field=models.BigIntegerField(default=None, null=True),
        ),
    ]
