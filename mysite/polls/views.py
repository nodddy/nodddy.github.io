from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy

from .forms import ExperimentForm, ParameterFormSet, ParameterForm, NoteForm, NoteFormSet, StepForm, StepFormSet
from .models import Parameter, Experiment


def index(request):
    context = {
        'experiment_list': Experiment.objects.order_by('-date'),
    }
    return render(request, 'polls/index.html', context)


class ExperimentCreateView(generic.CreateView):
    template_name = 'polls/add_experiment.html'
    form_class = ExperimentForm


class ParameterUpdateView(generic.UpdateView):
    template_name = 'polls/results.html'
    form_class = ExperimentForm
    model = Experiment
    success_url = ''

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        try:
            experiment = get_object_or_404(Experiment, id=self.kwargs['experiment_id'])
            self.object = experiment
        except KeyError:
            self.object = None

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        parameter_form = ParameterFormSet(instance=self.object)
        step_form = StepFormSet(instance=self.object)
        note_form = NoteFormSet(instance=self.object)
        return self.render_to_response(
            self.get_context_data(form=form,
                                  parameter_form=parameter_form,
                                  step_form=step_form,
                                  note_form=note_form))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """

        def delete_entry(request, form_instance):
            delete_entry_list = [key for key in request.POST.keys() if 'btn_delete' in key]
            if len(delete_entry_list) != 0:
                print(delete_entry_list)
                model_name, entry_id_from_form = delete_entry_list[0].split('-')[-1].split('.')

                entry_id_list = [item.pk for item in Parameter.objects.filter(experiment=form_instance).all()]
                try:
                    entry_id = entry_id_list[int(entry_id_from_form) - 1]
                    entry = Parameter.objects.get(experiment=form_instance, id=entry_id)
                    entry.delete()
                    return True
                except IndexError:
                    return True



        form_class = self.get_form_class()
        form = self.get_form(form_class)
        form_instance = get_object_or_404(Experiment, id=self.kwargs['experiment_id'])
        form.instance = form_instance
        parameter_form = ParameterFormSet(self.request.POST, instance=form_instance)
        step_form = StepFormSet(self.request.POST, instance=form_instance)
        note_form = NoteFormSet(self.request.POST, instance=form_instance)
        delete_entry_list = [key for key in request.POST.keys() if 'btn_delete' in key]
        if 'add_parameter_btn' in request.POST.keys():
            parameter_form.extra = +1
            self.success_url = reverse_lazy('polls:update_parameter', args=[form_instance.id])
        elif 'add_step_btn' in request.POST.keys():
            step_form.extra = +1
            self.success_url = reverse_lazy('polls:update_parameter', args=[form_instance.id])
        elif 'add_note_btn' in request.POST.keys():
            note_form.extra = +1
            self.success_url = reverse_lazy('polls:update_parameter', args=[form_instance.id])
        else:
            self.success_url = reverse_lazy('polls:detail', args=[form_instance.id])

        if delete_entry(request, form_instance):
            self.success_url = reverse_lazy('polls:update_parameter', args=[self.kwargs['experiment_id']])

        form_list = [parameter_form, step_form, note_form]
        valid_list = [child_form for child_form in form_list if
                      form.is_valid() and child_form.is_valid()]
        return self.form_valid(form, valid_list)

    def form_valid(self, form, valid_child_list):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        self.object = form.save()
        for child_form in valid_child_list:
            child_form.instance = self.object
            child_form.save()
        return HttpResponseRedirect(self.get_success_url())


def change(request, experiment_id, model_id, entry_id, form_id):
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    form_dict = {
        'step_form': StepForm,
        'note_form': NoteForm,
        'parameter_form': ParameterForm
    }
    if 'Abort' in request.POST.keys():
        return HttpResponseRedirect(reverse('polls:detail', args=(experiment.id,)))

    model_set = getattr(experiment, f'{model_id}_set')
    entry_instance = model_set.get(id=entry_id)
    form = form_dict[form_id](request.POST, instance=entry_instance)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('polls:detail', args=(experiment.id,)))
    form = form_dict[form_id](instance=entry_instance)
    return render(request, 'polls/change.html', {
        'experiment': experiment,
        'form': form,
        'entry_id': entry_id,
        'block_buttons': True, })


class ExperimentDetailView(generic.DetailView):
    template_name = 'polls/detail.html'

    def get_object(self):
        id_ = self.kwargs.get('experiment_id')
        return get_object_or_404(Experiment, id=id_)


class ExperimentDetailCreateView(generic.CreateView):
    template_name = 'polls/add.html'
    form_dict = {
        'step_form': StepForm,
        'note_form': NoteForm,
        'parameter_form': ParameterForm
    }

    def get_form_id(self):
        return self.kwargs.get('form_id')


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
    return render(request, 'polls/add_experiment.html', {'block_buttons': True,
                                                         'form': form,
                                                         'experiment_list': Experiment.objects.order_by('-date')})


def add(request, experiment_id, form_id=''):
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    form_dict = {
        'step_form': StepForm,
        'note_form': NoteForm,
        'parameter_form': ParameterForm
    }
    form = form_dict[form_id](request.POST or None)
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
                                              'block_buttons': True})


def delete(request, experiment_id, model_id, entry_id):
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    if request.method == 'POST' and 'delete' in request.POST:
        model_set = getattr(experiment, f'{model_id}_set')
        model_set.get(id=entry_id).delete()
    return HttpResponseRedirect(reverse('polls:detail', args=(experiment.id,)))
