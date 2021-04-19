from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.forms.models import inlineformset_factory
import re, urllib

from .forms import ExperimentForm, ParameterFormSet, ParameterForm, NoteForm, NoteFormSet, StepForm, StepFormSet, \
    SampleForm
from .models import Parameter, Experiment, Sample, Step


def index(request):
    context = {
        'experiment_list': Experiment.objects.order_by('-date'),
        'sample_list': Sample.objects.all()}
    return render(request, 'polls/index.html', context)


class ParameterUpdateView(generic.UpdateView):
    parent_model = None
    formset_widgets = {}
    formset = None
    object = None

    def dispatch(self, request, *args, **kwargs):
        self.template_name = kwargs.get('template_name')
        self.model = kwargs.get('model')
        self.parent_model = kwargs.get('parent_model', None)
        self.fields = kwargs.get('fields')
        self.formset_widgets = kwargs.get('formset_widgets', {})
        self.formset = inlineformset_factory(self.parent_model,
                                             self.model,
                                             fields=self.fields,
                                             extra=0,
                                             can_delete=False)
        return super(ParameterUpdateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        self.object is the parent instance (i.e. Experiment or Sample or Step) of the Paramenter instance
        """
        self.object = get_object_or_404(self.parent_model, id=self.kwargs['parent_id'])
        return self.render_to_response(self.get_context_data(parent_id=self.object.id,
                                                             parent=self.object,
                                                             formset=self.formset(instance=self.object, prefix='form')))

    def post(self, request, *args, **kwargs):
        delete_btn_identifier = re.search(r'btn_delete-\d+', urllib.parse.urlencode(request.POST))
        if delete_btn_identifier is not None:
            entry = get_object_or_404(self.model, id=delete_btn_identifier.group().split('-')[1])
            entry.delete()
            self.form_invalid(request)

        self.object = get_object_or_404(self.parent_model, id=self.kwargs['parent_id'])
        form = self.formset(self.request.POST, instance=self.object, prefix='form')
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(request)

    def form_valid(self, form):
        for f in form:
            new_f = f.save(commit=False)
            new_f.instance = self.object
            new_f.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, request):
        self.object = get_object_or_404(self.parent_model, id=self.kwargs['parent_id'])
        return self.render_to_response(self.get_context_data(form_invalid=True,
                                                             parent_id=self.object.id,
                                                             formset=self.formset(instance=self.object, prefix='form')))


class ChildUpdateView(ParameterUpdateView):
    child_model = None
    child_fields = {}
    child_formset = None
    object = None

    def dispatch(self, request, *args, **kwargs):
        self.model = kwargs.get('model')
        self.child_model = kwargs.get('child_model')
        self.child_fields = kwargs.get('child_fields')
        self.child_formset = inlineformset_factory(self.model,
                                                   self.child_model,
                                                   fields=self.child_fields,
                                                   extra=0,
                                                   can_delete=False)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object = get_object_or_404(self.model, id=self.kwargs['parent_id'])
        step_list = [value for value in self.model.objects.filter(experiment=self.object.id).in_bulk().values()]
        child_formset_list = [self.child_formset(instance=child_instance, prefix='child_form') for child_instance in
                              step_list]
        context['child_formset_list'] = child_formset_list
        return context

    def post(self, request, *args, **kwargs):
        self.object = get_object_or_404(self.parent_model, id=self.kwargs['parent_id'])
        step_list = [value for value in self.model.objects.filter(experiment=self.object.id).in_bulk().values()]
        child_formset_list = [self.child_formset(self.request.POST, instance=child_instance, prefix='child_form') for
                              child_instance in step_list]

        for step in step_list:
            for child_form in child_formset_list:
                if child_form.is_valid():
                    new_f = child_form.save(commit=False)
                    new_f.instance = step
                    new_f.save()
                else:
                    print(child_form.errors)
                    return super().form_invalid(request)
        return super().post(request, *args, **kwargs)


class ExperimentDetailView(generic.DetailView):
    template_name = 'polls/experiment-detail.html'
    object = None

    def get(self, request, *args, **kwargs):
        self.object = get_object_or_404(Experiment, id=self.kwargs['parent_id'])
        return self.render_to_response(self.get_context_data(parent=self.object,
                                                             parent_id=self.object.id))


class SampleDetailView(generic.DetailView):
    template_name = 'polls/sample-detail.html'
    object = None

    def get(self, request, *args, **kwargs):
        self.object = get_object_or_404(Sample, id=self.kwargs['parent_id'])
        return self.render_to_response(self.get_context_data(parent=self.object,
                                                             parent_id=self.object.id))
