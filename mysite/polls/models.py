from django.db import models


class Experiment(models.Model):
    experiment_name = models.CharField(max_length=200)
    date = models.DateTimeField('Date of experiment')

    def __str__(self):
        return self.experiment_name


class Parameter(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    parameter_name = models.CharField(max_length=200)
    parameter_value = models.FloatField(default=None)
    parameter_unit = models.CharField(max_length=200)

    def __str__(self):
        return self.parameter_name


class Observation(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    observation_image = models.ImageField
    observation_text = models.CharField(max_length=400)


class Note(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    note_text = models.CharField(max_length=400)


class Data(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    data_name = models.CharField(max_length=200)
    data_type = models.CharField(max_length=200)
    data_file = models.FileField
    data_file_name = models.CharField(max_length=200)
    data_file_type = models.CharField(max_length=200)
    data_file_delimiter = models.CharField(max_length=200)

    def __str__(self):
        return self.data_name
