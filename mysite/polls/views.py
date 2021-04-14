from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse

from .forms import ExperimentForm, ParameterForm, NoteForm, StepForm
from .models import Parameter, Experiment


def index(request):
    context = {
        'experiment_list': Experiment.objects.order_by('-date'),
    }
    return render(request, 'polls/index.html', context)


def detail(request, experiment_id):
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    context = {
        'experiment': experiment,
    }

    return render(request, 'polls/detail.html', context)


def add_experiment(request):
    form = ExperimentForm(request.POST)
    if form.is_valid():
        form.save()
    return render(request, 'polls/add_experiment.html', {'block_add': True,
                                                         'form': form,
                                                         'experiment_list': Experiment.objects.order_by('-date')})


def add(request, experiment_id, form_id=''):
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    form_dict = {
        'step_form': StepForm,
        'note_form': NoteForm,
        'parameter_form': ParameterForm
    }
    form = form_dict[form_id](request.POST)
    if 'Abort' in request.POST.keys():
        return HttpResponseRedirect(reverse('polls:detail', args=(experiment.id,)))
    if form.is_valid():
        new_parameter = form.save(commit=False)
        new_parameter.experiment_id = experiment_id
        new_parameter.save()
    form = form_dict[form_id]()
    return render(request, 'polls/add.html', {'form_id': form_id,
                                              'form': form,
                                              'experiment': experiment,
                                              'block_add': True})


def delete(request, experiment_id, model_id, entry_id):
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    if request.method == 'POST' and 'delete' in request.POST:
        model_set = getattr(experiment, f'{model_id}_set')
        model_set.get(id=entry_id).delete()
    return HttpResponseRedirect(reverse('polls:detail', args=(experiment.id,)))