from django.db import models
from django.urls import reverse
import datetime

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


class Data(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    file = models.FileField
    file_name = models.CharField(max_length=200)
    file_type = models.CharField(max_length=200)
    file_delimiter = models.CharField(max_length=200)

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
