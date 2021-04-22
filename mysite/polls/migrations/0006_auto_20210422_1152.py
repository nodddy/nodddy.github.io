# Generated by Django 3.2 on 2021-04-22 09:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0005_auto_20210421_1618'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='data',
            name='file_name',
        ),
        migrations.RemoveField(
            model_name='data',
            name='file_type',
        ),
        migrations.AddField(
            model_name='data',
            name='file',
            field=models.FileField(default=None, upload_to='experiment/files/'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='data',
            name='sample',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sample_name', to='polls.sample'),
        ),
        migrations.AlterField(
            model_name='data',
            name='experiment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='experiment_data', to='polls.experiment'),
        ),
        migrations.AlterField(
            model_name='data',
            name='file_delimiter',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='data',
            name='type',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='parameter',
            name='unit',
            field=models.CharField(blank=True, default=None, max_length=200),
            preserve_default=False,
        ),
    ]
