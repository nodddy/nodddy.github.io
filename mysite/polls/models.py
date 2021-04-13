from django.db import models


class Experiment(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateTimeField('Date of experiment', blank=True, null=True)
    sample = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name


class Parameter(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    value = models.FloatField(default=None)
    unit = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Note(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    text = models.CharField(max_length=400)


class Data(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    file = models.FileField
    file_name = models.CharField(max_length=200)
    file_type = models.CharField(max_length=200)
    file_delimiter = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Step(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    note = models.CharField(max_length=200, blank=True)
    text = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.experiment.name}.{self.text}'


class StepExperiment(models.Model):
    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class StepParameter(models.Model):
    stepexperiment = models.ForeignKey(StepExperiment, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    value = models.FloatField(default=None)
    unit = models.CharField(max_length=200)

    def __str__(self):
        return self.name
