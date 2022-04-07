# Generated by Django 2.2.16 on 2022-02-08 00:32

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compasui', '0005_auto_20220201_0224'),
    ]

    operations = [
        migrations.AddField(
            model_name='singlebinaryjob',
            name='common_envelope_alpha',
            field=models.FloatField(blank=True, default=1.0, help_text='--common-envelope-alpha: Common Envelope efficiency alpha, Value > 0', null=True, validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AddField(
            model_name='singlebinaryjob',
            name='common_envelope_lambda',
            field=models.FloatField(blank=True, default=0.1, help_text='--common-envelope-lambda: Common Envelope lambda, Value > 0', null=True, validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AddField(
            model_name='singlebinaryjob',
            name='common_envelope_lambda_prescription',
            field=models.CharField(blank=True, choices=[('LAMBDA_FIXED', 'LAMBDA_FIXED'), ('LAMBDA_KRUCKOW', 'LAMBDA_KRUCKOW'), ('LAMBDA_LOVERIDGE', 'LAMBDA_LOVERIDGE'), ('LAMBDA_NANJING', 'LAMBDA_NANJING'), ('LAMBDA_DEWI', 'LAMBDA_DEWI')], default='LAMBDA_NANJING', help_text='--common-envelope-lambda-prescription: CE lambda prescription', max_length=55, null=True),
        ),
    ]