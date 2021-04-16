from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.forms.models import inlineformset_factory
import re, urllib

from .forms import ExperimentForm, ParameterFormSet, ParameterForm, NoteForm, NoteFormSet, StepForm, StepFormSet, \
    SampleForm
from .models import Parameter, Experiment, Sample


def index(request):
    context = {
        'experiment_list': Experiment.objects.order_by('-date'),
    }
    return render(request, 'polls/index.html', context)


class ParameterUpdateView(generic.UpdateView):
    template_name = 'polls/parameter-update.html'
    model = Parameter
    parent_model = Sample
    fields = ['name', 'value', 'unit']
    success_url = ''
    object = None
    formset = inlineformset_factory(parent_model,
                                    model,
                                    fields=fields,
                                    extra=1,
                                    can_delete=True)

    def get(self, request, *args, **kwargs):
        """
        self.object is the parent instance (i.e. Experiment or Sample or Step) of the Paramenter instance
        """
        self.object = get_object_or_404(self.parent_model, id=self.kwargs['parent_id'])
        return self.render_to_response(self.get_context_data(parent_id=self.object.id,
                                                             formset=self.formset(instance=self.object)))

    def post(self, request, *args, **kwargs):
        def delete_entry(request):
            delete_btn_identifier = re.search(r'btn_delete\d', urllib.parse.urlencode(request.POST))
            if delete_btn_identifier is not None:
                entry = get_object_or_404(self.model, id=delete_btn_identifier.group()[-1])
                entry.delete()
                return self.form_invalid(request)
        def add_row(request):
            add_row_btn_identifier = re.search(r'btn_add_row\d', urllib.parse.urlencode(request.POST))
            if add_row_btn_identifier is not None:
                return self.form_valid(request)
        self.object = get_object_or_404(self.parent_model, id=self.kwargs['parent_id'])
        form = self.formset(request.POST, instance=self.object)

        delete_entry(request)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(request)

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(reverse('polls:sample-detail', kwargs={'parent_id': self.object.id}))

    def form_invalid(self, request):
        return self.render_to_response(self.get_context_data(form_invalid=True,
                                                             parent_id=self.object.id,
                                                             formset=self.formset(instance=self.object)))


class ExperimentUpdateView(generic.UpdateView):
    template_name = 'polls/results.html'
    form_class = ExperimentForm
    model = Experiment

    def get(self, request, *args, **kwargs):
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
        return self.render_to_response(self.get_context_data(form=form,
                                                             parameter_form=parameter_form,
                                                             step_form=step_form,
                                                             note_form=note_form))

    def post(self, request, *args, **kwargs):
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
        try:
            form_instance = get_object_or_404(self.model, id=self.kwargs['experiment_id'])
        except KeyError:
            form_instance = self.model.objects.create()

        form.instance = form_instance

        parameter_form = ParameterFormSet(self.request.POST, instance=form_instance)
        step_form = StepFormSet(self.request.POST, instance=form_instance)
        note_form = NoteFormSet(self.request.POST, instance=form_instance)

        if not [key for key in request.POST.keys() if 'btn_delete' in key]:
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
        self.object = form.save()
        for child_form in valid_child_list:
            child_form.instance = self.object
            child_form.save()
        return HttpResponseRedirect(self.get_success_url())


class ExperimentDetailView(generic.DetailView):
    template_name = 'polls/detail.html'

    def get_object(self):
        id_ = self.kwargs.get('experiment_id')
        return get_object_or_404(Experiment, id=id_)


class SampleDetailView(generic.DetailView):
    template_name = 'polls/sample-detail.html'

    def get(self, request, *args, **kwargs):
        self.object = get_object_or_404(Sample, id=self.kwargs['parent_id'])
        return self.render_to_response(self.get_context_data(parent=self.object))
