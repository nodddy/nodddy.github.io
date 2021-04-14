# Generated by Django 3.2 on 2021-04-12 05:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('experiment_name', models.CharField(max_length=200)),
                ('date', models.DateTimeField(blank=True, null=True, verbose_name='Date of experiment')),
                ('sample', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.CharField(max_length=200)),
                ('text', models.CharField(max_length=200)),
                ('experiment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.experiment')),
            ],
        ),
        migrations.CreateModel(
            name='StepExperiment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('step', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.step')),
            ],
        ),
        migrations.CreateModel(
            name='StepParameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('value', models.FloatField(default=None)),
                ('unit', models.CharField(max_length=200)),
                ('stepexperiment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.stepexperiment')),
            ],
        ),
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parameter_name', models.CharField(max_length=200)),
                ('parameter_value', models.FloatField(default=None)),
                ('parameter_unit', models.CharField(max_length=200)),
                ('experiment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.experiment')),
            ],
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note_text', models.CharField(max_length=400)),
                ('experiment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.experiment')),
            ],
        ),
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_name', models.CharField(max_length=200)),
                ('data_type', models.CharField(max_length=200)),
                ('data_file_name', models.CharField(max_length=200)),
                ('data_file_type', models.CharField(max_length=200)),
                ('data_file_delimiter', models.CharField(max_length=200)),
                ('experiment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.experiment')),
            ],
        ),
    ]