# Generated by Django 3.2 on 2021-04-27 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0004_alter_file_pdf'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='img',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
