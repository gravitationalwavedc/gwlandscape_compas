# Generated by Django 2.2.16 on 2022-02-10 09:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('compasui', '0011_auto_20220210_0900'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='singlebinaryjob',
            name='pair_instability_supernovae',
        ),
        migrations.RemoveField(
            model_name='singlebinaryjob',
            name='pulsational_pair_instability_supernovae',
        ),
    ]
