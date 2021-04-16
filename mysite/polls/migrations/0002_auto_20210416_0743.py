# Generated by Django 3.2 on 2021-04-16 05:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='step',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='step_note', to='polls.step'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='parameter',
            name='step',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='step_parameter', to='polls.step'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='note',
            name='experiment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='experiment_note', to='polls.experiment'),
        ),
        migrations.AlterField(
            model_name='note',
            name='sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sample_note', to='polls.sample'),
        ),
        migrations.AlterField(
            model_name='parameter',
            name='experiment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='experiment_parameter', to='polls.experiment'),
        ),
        migrations.AlterField(
            model_name='parameter',
            name='sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sample_parameter', to='polls.sample'),
        ),
    ]