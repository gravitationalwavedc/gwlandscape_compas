# Generated by Django 3.2.13 on 2022-08-16 03:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('compasui', '0014_auto_20220609_0458'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdvancedParameter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=55)),
                ('value', models.CharField(blank=True, max_length=100, null=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                          related_name='advanced_parameter', to='compasui.compasjob')),
            ],
        ),
        migrations.CreateModel(
            name='BasicParameter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=55)),
                ('value', models.CharField(blank=True, max_length=100, null=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                          related_name='basic_parameter', to='compasui.compasjob')),
            ],
        ),
        migrations.RemoveField(
            model_name='dataparameter',
            name='data',
        ),
        migrations.RemoveField(
            model_name='dataparameter',
            name='job',
        ),
        migrations.RemoveField(
            model_name='search',
            name='job',
        ),
        migrations.RemoveField(
            model_name='searchparameter',
            name='job',
        ),
        migrations.RemoveField(
            model_name='searchparameter',
            name='search',
        ),
        migrations.DeleteModel(
            name='Data',
        ),
        migrations.DeleteModel(
            name='DataParameter',
        ),
        migrations.DeleteModel(
            name='Search',
        ),
        migrations.DeleteModel(
            name='SearchParameter',
        ),
    ]
