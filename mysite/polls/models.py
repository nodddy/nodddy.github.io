from django.db import models
from django.urls import reverse


class Sample(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Experiment(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    date = models.DateField('Date of experiment', blank=True, null=True)

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
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, null=True, blank=True)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, blank=True, null=True)
    note = models.CharField(max_length=200, blank=True)
    text = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.experiment.name}.{self.text}'


class Note(models.Model):
    step = models.ForeignKey(Step, on_delete=models.CASCADE, related_name='step_note', blank=True, null=True)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name='sample_note', blank=True, null=True)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='experiment_note', blank=True,
                                   null=True)
    text = models.CharField(max_length=400)


class Parameter(models.Model):
    step = models.ForeignKey(Step, on_delete=models.CASCADE, related_name='step_parameter', blank=True, null=True)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name='sample_parameter', blank=True, null=True)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='experiment_parameter',
                                   blank=True, null=True)
    name = models.CharField(max_length=200)
    value = models.FloatField(default=None)
    unit = models.CharField(max_length=200)

    def __str__(self):
        return self.name
