from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse

from .forms import ParameterForm, NoteForm, StepForm
from .models import Parameter, Experiment


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_experiment_list'

    def get_queryset(self):
        """Return experiments based on latest by time"""
        return Experiment.objects.order_by('-date')


def detail(request, experiment_id):
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    context = {
        'experiment': experiment,
    }

    return render(request, 'polls/detail.html', context)


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


def delete(request, experiment_id, form_id):
    print(form_id)
    pk = form_id
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    if request.method == 'POST' and 'delete' in request.POST:
        pass
    # experiment.object.filter().delete()
    return HttpResponseRedirect(reverse('polls:detail', args=(experiment.id,)))
