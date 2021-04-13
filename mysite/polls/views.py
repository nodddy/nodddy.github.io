from django.shortcuts import render, get_object_or_404
from django.views import generic

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



def add_parameter(request, experiment_id, modelform):
    return add_data_to_model(request, experiment_id, modelform)

def add_data_to_model(request, experiment_id, modelform):
    modeldict = {
        'parameter': ParameterForm(request.POST),
        'note': NoteForm(request.POST),
        'step': StepForm(request.POST),
    }
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    form = modeldict[modelform]
    if form.is_valid():
        new_parameter = form.save(commit=False)
        new_parameter.experiment_id = experiment_id
        new_parameter.save()
    if 'Abort' in request.POST.keys():
        return render(request, 'polls/detail.html', {'experiment': experiment})

    return render(request, f'polls/add_{modelform}_form.html', {'form': form,
                                                                'experiment': experiment,
                                                                'block_add': True})
