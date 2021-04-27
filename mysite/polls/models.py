from django.shortcuts import get_object_or_404
from django.http import Http404
import os
from django.db import models
from django.urls import reverse
import datetime
import pandas as pd
import pdfkit
from pathlib import Path
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from .signals import mute_signals


class Sample(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('polls:sample-detail', kwargs={'parent_id': self.id})


class Experiment(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.PROTECT, related_name='experiments')
    name = models.CharField(max_length=200)
    date = models.DateField('Date of experiment', default=datetime.datetime.now)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('polls:experiment-detail', kwargs={'parent_id': self.id})


class File(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='experiment_files', null=True,
                                   blank=True)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name='sample_name', null=True, blank=True)
    name = models.CharField(max_length=200, blank=True)
    type = models.CharField(max_length=200, blank=True, null=True,
                            choices=[('txt', 'txt'), ('csv', 'csv'), ('pdf', 'pdf'), ('img', 'image'), ('etc', 'other')]
                            )
    upload_folder = 'experiment/files/'
    file = models.FileField(upload_to=upload_folder, null=True)
    pdf = models.FileField(null=True, blank=True)
    csv = models.JSONField(blank=True, null=True)
    csv_plot = models.CharField(max_length=200, blank=True, null=True)
    file_delimiter = models.CharField(max_length=200, blank=True, null=True,
                                      choices=[('\t', 'tabstop'), ('.', '.'), (',', ','), (';', ';')]
                                      )

    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    pdf_config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    pdf_options = {
        'margin-top': '0.1in',
        'margin-right': '0.1in',
        'margin-bottom': '0.1in',
        'margin-left': '0.1in',
        'minimum-font-size': 18,
        'encoding': "UTF-8"
    }

    def __str__(self):
        return self.name

    def absolute_path(self, name) -> str:
        """
        Generates the absolute local path of a file.
        :param name: name attribute of file field
        :return: the path
        """
        return f'{Path(self.file.storage.location).as_posix()}/{self.upload_folder}{name}'

    @mute_signals(pre_save)
    def delete(self, *args, **kwargs):
        """
        Deletes the associated file with self.file along with its pdf file. Also does not call save signals.
        """
        self.file.delete()
        if (pdf := self.pdf):
            pdf.delete()

        super().delete(*args, **kwargs)

    @staticmethod
    def txt_to_pdf(instance, file_name):
        """
        Takes file_instance and generates a pdf file from the txt file, then saves it to the file_instance's
        path with .pdf added.
        :return: A string with the pdf file path
        """
        output_path = f'{instance.absolute_path(file_name)}.pdf'
        pdfkit.from_string(instance.file._file.read().decode('utf-8'), output_path, configuration=instance.pdf_config,
                           options=instance.pdf_options)
        return f'{instance.upload_folder}{file_name}.pdf'

    @staticmethod
    def csv_to_pdf(instance, file_name, file):
        """
        Gets the csv attribute from file model and then converts it in form of a JSON string
        to a pandas df and then html with specified CSS in 'pd_options.
        Finally the html gets converted to pdf and saved to the file_instance path with .pdf added.
        :param file_instance: the instance of file model
        :return: A string with the pdf file path
        """

        def reduce_df(dataframe):
            if (df_length := len(dataframe)) > 10000:
                return dataframe.iloc[::20]
            elif df_length > 1000:
                return dataframe.iloc[::10]
            elif df_length > 100:
                return dataframe.iloc[::2]
            else:
                return dataframe

        pd.set_option('colheader_justify', 'center')
        pd_options = '<html>' \
                     '<meta charset="utf-8">' \
                     '<meta name="viewport" content="width=device-width, initial-scale=1">' \
                     '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/css/bootstrap.min.css"' \
                     ' rel="stylesheet"integrity="sha384-eOJMYsd53ii+scO/bJGFsiCZc+5NDVN2yr8+0RDqr0Ql0h+rP48ckxlpbzKgwra6"' \
                     ' crossorigin="anonymous">' \
                     '<body> {table} </body>' \
                     '</html>'  # bootstrap CSS is loaded from website

        df = pd.read_csv(file, delimiter=instance.file_delimiter)
        csv = reduce_df(df).to_json()
        instance.csv = csv
        df_html = pd_options.format(table=pd.read_json(csv).to_html(na_rep='', classes='table'))
        output_path = f'{instance.absolute_path(file_name)}.pdf'
        pdfkit.from_string(df_html, output_path, configuration=instance.pdf_config, options=instance.pdf_options)
        return f'{instance.upload_folder}{file_name}.pdf'


@receiver(pre_save, sender=File)
def update_view_files(sender, instance, **kwargs):
    """
    Signal receiver for the save of file upload data and data conversion depending on file type. Only saves the data
    if the file to be saved is new or different from the old one.
    Saves the file as todays date along with a random string.
    :param sender: model class which gets saved
    :param instance: model instance
    """

    new_file_name = f'{str(datetime.date.today())}_{get_random_string(10)}'
    file = instance.file._file
    try:
        obj = get_object_or_404(sender, pk=instance.pk)
        if obj.type == instance.type and obj.file_delimiter == instance.file_delimiter and file is None:
            return
        else:
            if file is None:
                new_file_name = obj.file.name.split('/')[-1]
                file = instance.absolute_path(new_file_name)
            else:
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
    elif instance.type == 'csv':
        instance.pdf.name = sender.csv_to_pdf(instance, new_file_name, file)
    elif instance.type == 'txt':
        instance.pdf.name = sender.txt_to_pdf(instance, new_file_name)
    return


class Plot(models.Model):
    file = models.ForeignKey(File, on_delete=models.PROTECT, related_name='file_plots', null=True, blank=True)
    sample = models.ForeignKey(Sample, on_delete=models.PROTECT, related_name='sample_plots', null=True, blank=True)
    name = models.CharField(max_length=200)
    data = models.FileField()
    img = models.ImageField()  # vielleicht jeden plot als bild abspeichern oder jeweils neu plotten. Bild speichern wenn download gewollt ist

    def __str__(self):
        return self.name


class Step(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='experiment_steps', blank=True,
                                   null=True)
    note = models.CharField(max_length=200, blank=True)
    text = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.experiment.name}.{self.text}'


class Note(models.Model):
    step = models.ForeignKey(Step, on_delete=models.CASCADE, related_name='step_notes', blank=True, null=True)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name='sample_notes', blank=True, null=True)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='experiment_notes', blank=True,
                                   null=True)
    text = models.CharField(max_length=400)


class Parameter(models.Model):
    step = models.ForeignKey(Step, on_delete=models.CASCADE, related_name='step_parameters', blank=True, null=True)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name='sample_parameters', blank=True,
                               null=True)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='experiment_parameters',
                                   blank=True, null=True)
    name = models.CharField(max_length=200)
    value = models.CharField(max_length=200, blank=True, null=True)
    unit = models.CharField(max_length=200, blank=True, null=False)

    def __str__(self):
        return self.name
