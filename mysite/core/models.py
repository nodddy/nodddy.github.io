from django.shortcuts import get_object_or_404
from django.http import Http404
from django.db import models
from django.db.models.signals import pre_save
from django.urls import reverse
from django.dispatch import receiver
from django.utils.crypto import get_random_string

import datetime
from pathlib import Path

from .signals import mute_signals
from .db_utils import convert_csv_to_pdf, txt_to_pdf


class Sample(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('core:sample-detail', kwargs={'parent_id': self.id})


class Experiment(models.Model):
    sample = models.ForeignKey(
        Sample,
        on_delete=models.PROTECT,
        related_name='experiments'
    )
    name = models.CharField(max_length=200)
    date = models.DateField('Date of experiment', default=datetime.datetime.now)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('core:experiment-detail', kwargs={'parent_id': self.id})


class File(models.Model):
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name='experiment_files',
        null=True,
        blank=True
    )
    sample = models.ForeignKey(
        Sample,
        on_delete=models.CASCADE,
        related_name='sample_name',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=200, blank=True)

    upload_folder = 'experiment/files/'
    file = models.FileField(upload_to=upload_folder, null=True)
    pdf = models.FileField(null=True, blank=True)
    img = models.ImageField(null=True, blank=True)
    csv = models.JSONField(null=True, blank=True)
    csv_plot = models.CharField(max_length=200, blank=True, null=True)
    type = models.CharField(max_length=200, blank=True, null=True, choices=[
        ('txt', 'txt'),
        ('csv', 'csv'),
        ('pdf', 'pdf'),
        ('img', 'image'),
        ('etc', 'other')
    ])
    file_delimiter = models.CharField(max_length=200, blank=True, null=True, choices=[
        ('\t', 'tabstop'),
        ('.', '.'),
        (',', ','),
        (';', ';')
    ])

    def __str__(self):
        return self.name

    def absolute_path(self, name) -> str:
        """ Generates the absolute local path of a file. """
        return f'{Path(self.file.storage.location).as_posix()}/{self.upload_folder}{name}'

    @mute_signals(pre_save)
    def delete(self, *args, **kwargs):
        """
        Deletes the associated file with self.file along with its pdf or img file. Also does not call save signals.
        """
        self.file.delete()
        if pdf := self.pdf:
            pdf.delete()
        if img := self.img:
            img.delete()

        return super().delete(*args, **kwargs)


@receiver(pre_save, sender=File)
def update_view_files(sender, instance, **kwargs):
    """
    Signal receiver for the save of file upload data and data conversion depending on file type.
    Creates new file and deletes the old one if the file changes.
    Recreates the pdf file if file.type or file.file_delimiter changes with the new attributes.
    Saves the file as today's date along with a random string.
    :param sender: model class which gets saved
    :param instance: model input_instance
    """

    new_file_name = f'{str(datetime.date.today())}_{get_random_string(10)}'
    file = instance.file._file  # This is the uploaded file in memory

    try:
        obj = get_object_or_404(sender, pk=instance.pk)
        if obj.type == instance.type and obj.file_delimiter == instance.file_delimiter and file is None:
            return  # Returns if nothing or only File.name changed

        if file is None:  # If no new file was selected
            new_file_name = obj.file.name.split('/')[-1]
            file = instance.absolute_path(new_file_name)
        else:  # If new file is uploaded, deletes the old file and pdf
            obj.file.delete()
            if obj.pdf:
                obj.pdf.delete()
    except Http404:
        if file is None:
            return

    # TODO: Add file type validation for file upload in views.py
    instance.file.name = f'{new_file_name}'
    if instance.type == 'pdf':
        instance.pdf.name = f'{instance.upload_folder}{new_file_name}'
    elif instance.type == 'img':
        instance.img.name = f'{instance.upload_folder}{new_file_name}'
    elif instance.type == 'csv':
        instance.pdf.name = convert_csv_to_pdf(instance, new_file_name, file)
    elif instance.type == 'txt':
        instance.pdf.name = txt_to_pdf(instance, new_file_name)
    return


class Plot(models.Model):
    file = models.ForeignKey(
        File,
        on_delete=models.PROTECT,
        related_name='file_plots',
        null=True,
        blank=True
    )
    sample = models.ForeignKey(
        Sample,
        on_delete=models.PROTECT,
        related_name='sample_plots',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=200)
    data = models.FileField()
    img = models.ImageField()

    def __str__(self):
        return self.name


class Step(models.Model):
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name='experiment_steps',
        blank=True,
        null=True
    )
    note = models.CharField(max_length=200, blank=True)
    text = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.experiment.name}.{self.text}'


class Note(models.Model):
    step = models.ForeignKey(
        Step,
        on_delete=models.CASCADE,
        related_name='step_notes',
        blank=True,
        null=True
    )
    sample = models.ForeignKey(
        Sample,
        on_delete=models.CASCADE,
        related_name='sample_notes',
        blank=True,
        null=True
    )
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name='experiment_notes',
        blank=True,
        null=True
    )
    text = models.CharField(max_length=400)


class Parameter(models.Model):
    step = models.ForeignKey(
        Step,
        on_delete=models.CASCADE,
        related_name='step_parameters',
        blank=True,
        null=True
    )
    sample = models.ForeignKey(
        Sample,
        on_delete=models.CASCADE,
        related_name='sample_parameters',
        blank=True,
        null=True
    )
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name='experiment_parameters',
        blank=True,
        null=True
    )
    name = models.CharField(max_length=200)
    value = models.CharField(max_length=200, blank=True, null=True)
    unit = models.CharField(max_length=200, blank=True, null=False)

    def __str__(self):
        return self.name
