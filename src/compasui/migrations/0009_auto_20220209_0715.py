# Generated by Django 2.2.16 on 2022-02-09 07:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('compasui', '0008_auto_20220209_0659'),
    ]

    operations = [
        migrations.RenameField(
            model_name='singlebinaryjob',
            old_name='Kick_velocity_distribution',
            new_name='kick_velocity_distribution',
        ),
    ]