# Generated by Django 2.2.16 on 2021-08-02 06:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CompasJob",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("user_id", models.IntegerField()),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, null=True)),
                ("creation_time", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now_add=True)),
                ("private", models.BooleanField(default=False)),
                (
                    "job_controller_id",
                    models.IntegerField(blank=True, default=None, null=True),
                ),
                ("is_ligo_job", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="Data",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "data_choice",
                    models.CharField(
                        choices=[["simulated", "Simulated"], ["real", "Real"]],
                        default="real",
                        max_length=55,
                    ),
                ),
                (
                    "source_dataset",
                    models.CharField(
                        blank=True,
                        choices=[["o1", "O1"], ["o2", "O2"], ["o3", "O3"]],
                        default="o1",
                        max_length=2,
                        null=True,
                    ),
                ),
                (
                    "job",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="data",
                        to="compasui.CompasJob",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Label",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50)),
                ("description", models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Search",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "job",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="search",
                        to="compasui.CompasJob",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SearchParameter",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=55)),
                ("value", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "job",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="search_parameter",
                        to="compasui.CompasJob",
                    ),
                ),
                (
                    "search",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="parameter",
                        to="compasui.Search",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DataParameter",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=55)),
                ("value", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "data",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="parameter",
                        to="compasui.Data",
                    ),
                ),
                (
                    "job",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="data_parameter",
                        to="compasui.CompasJob",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="compasjob",
            name="labels",
            field=models.ManyToManyField(to="compasui.Label"),
        ),
        migrations.AlterUniqueTogether(
            name="compasjob",
            unique_together={("user_id", "name")},
        ),
    ]
