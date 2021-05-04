from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.http import HttpResponseRedirect
from django.forms.models import inlineformset_factory
import re, urllib
import json

from .models import Experiment, Sample, File
from .forms import ExperimentForm
from .view_classes import UpdateCreateView


def index(request):
    """
    First site. Displays all experiments in chronological order. Displays all samples with atleast one associated experiment.
    """
    context = {
        'experiment_list': Experiment.objects.order_by('-date'),
        'sample_list': Sample.objects.exclude(experiments=None)}
    return render(request, 'core/index.html', context)


class ExperimentDetailView(generic.DetailView):
    """
    View for the Experiment with all its child models (i.e. Parameter).
    """
    template_name = 'core/experiment-detail.html'
    object = None

    def get(self, request, *args, **kwargs):
        """
        Takes the parent_id (experiment.id) from url and gets the input_instance object, which gets returned in context along
        with the input_instance id (for some reason its also required for proper function)
        """
        self.object = get_object_or_404(Experiment, id=self.kwargs['parent_id'])
        return self.render_to_response(self.get_context_data(parent=self.object, parent_id=self.object.id))


class SampleDetailView(generic.DetailView):
    """
    View for the Sample with all its child models (i.e. Parameter) and a link to its experiments.
    """
    template_name = 'core/sample-detail.html'
    object = None

    def get(self, request, *args, **kwargs):
        """
        Takes the parent_id (experiment.id) from url and gets the input_instance object, which gets returned in context along
        with the input_instance id (for some reason its also required for proper function)
        """
        self.object = get_object_or_404(Sample, id=self.kwargs['parent_id'])
        return self.render_to_response(self.get_context_data(parent=self.object, parent_id=self.object.id))


class ExperimentUpdateView(UpdateCreateView):
    """
    Updates the experiment input_instance when a parent_id is given in the url or it creates a new input_instance.
    Along with the form for Experiment model it asks for the Sample, which gets associated or created if its not in the DB.
    """

    def dispatch(self, request, formset=None, *args, **kwargs):
        return super(ExperimentUpdateView, self).dispatch(request, *args, formset=ExperimentForm, **kwargs)

    def form_valid(self, formset, request=None):
        form_instance = formset.save(commit=False)
        form_instance.sample, created = Sample.objects.get_or_create(name=request.POST['sample_name'])
        form_instance.save()
        if self.success_url is None:
            self.success_url = get_object_or_404(Experiment, id=form_instance.id).get_absolute_url()
        return HttpResponseRedirect(self.get_success_url())


class ParameterUpdateView(UpdateCreateView):
    formset_widgets = {}
    extra = int()

    def get_formset(self):
        return inlineformset_factory(
            self.parent_model,
            self.model,
            fields=self.fields,
            widgets=self.formset_widgets,
            extra=self.extra,
            can_delete=False,
        )

    def dispatch(self, request, *args, **kwargs):
        self.extra = kwargs.get('extra', 1)
        self.formset_widgets = kwargs.get('formset_widgets', {})
        return super(ParameterUpdateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.formset = self.get_formset()
        return super(ParameterUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.formset = self.get_formset()
        delete_btn_identifier = re.search(r'btn_delete-\d+', urllib.parse.urlencode(request.POST))
        if delete_btn_identifier is not None:
            entry = get_object_or_404(self.model, id=delete_btn_identifier.group().split('-')[1])
            entry.delete()
            return HttpResponseRedirect(request.path)
        else:
            return super(ParameterUpdateView, self).post(request, *args, **kwargs)


class ChildUpdateView(ParameterUpdateView):
    child_model = None
    child_fields = {}
    child_formset = None

    def dispatch(self, request, *args, **kwargs):
        self.model = kwargs.get('model')
        self.child_model = kwargs.get('child_model')
        self.child_fields = kwargs.get('child_fields')
        self.child_formset = inlineformset_factory(
            self.model,
            self.child_model,
            fields=self.child_fields,
            extra=1,
            can_delete=False
        )

        return super().dispatch(request, *args, **kwargs)

    def get_child_formsets(self, parent_list):
        return [self.child_formset(
            instance=child_instance,
            prefix=f'child_form{index}'
        ) for index, child_instance in enumerate(parent_list)]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        steps = self.model.objects.filter(experiment=self.get_object().id).in_bulk().values()
        context.update(child_formset_list=self.get_child_formsets(steps))
        return context

    def post(self, request, *args, **kwargs):
        delete_btn_identifier = re.search(r'btn_delete_child-\d+', urllib.parse.urlencode(request.POST))
        if delete_btn_identifier is not None:
            entry = get_object_or_404(self.child_model, id=delete_btn_identifier.group().split('-')[1])
            entry.delete()
            return HttpResponseRedirect(request.path)

        steps = self.model.objects.filter(experiment=self.get_object().id).in_bulk().values()
        for child_form in self.get_child_formsets(steps):
            if child_form.is_valid():
                child_form.save()
            else:
                return HttpResponseRedirect(request.path)
        return super().post(request, *args, **kwargs)


class FileView(generic.DetailView):
    template_name = 'core/file-viewer.html'
    object = None
    file = None

    def get_context_data(self, *args, **kwargs):
        """
        Takes the parent_id (experiment.id) from url and gets the input_instance object, which gets returned in context along
        with the input_instance id (for some reason its also required for proper function)
        """
        self.object = get_object_or_404(Experiment, id=self.kwargs['parent_id'])
        self.file = get_object_or_404(File, id=self.kwargs['file_id'])
        x_header = kwargs.get('x_header')
        y_header = kwargs.get('y_header')
        context = super().get_context_data(**kwargs)
        context.update({
            'parent': self.object,
            'parent_id': self.object.id,
            'input_file_name': self.file.name,
        })

        if file_type := kwargs.get('file_type') =='csv':
            csv_str = json.loads(self.file.csv)
            if x_header is not None:
                plot_data = {key: csv_str[key] for key in [x_header, y_header]}
            elif self.file.csv_plot is not None:
                plot_data = {key: csv_str[key] for key in eval(self.file.csv_plot)}
            else:
                plot_data = {key: csv_str[key] for key in [*csv_str.keys()][0:2]}

            context['plot_data'], context['x_label'], context['y_label'] = self.json_to_chart_data(plot_data)
            return context.update({
                'header': [*json.loads(self.file.csv).keys()],
                'plot': True
            })
        if file_type == 'pdf':

            return context.update({
                'file_url': self.file.pdf.url,
                'pdf': True
            })
        if file_type == 'img':
            return context.update({
                'file_url': self.file.img.url,
                'img': True
            })

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.file = get_object_or_404(File, id=self.kwargs['file_id'])
        if 'save_plot' in request.POST.keys():
            self.file.csv_plot = [request.POST['x_select'], request.POST['y_select']]
            self.file.save()
        return self.render_to_response(self.get_context_data(
            x_header=request.POST['x_select'],
            y_header=request.POST['y_select']
        ))

    @staticmethod
    def json_to_chart_data(json_str):
        header_list = [*json_str.keys()]
        data_list1 = [v.values() for v in json_str.values()]
        if len(header_list) == 2:
            data_list = [{'x': a, 'y': b} for a, b in zip(data_list1[0], data_list1[1])]
            return [data_list, header_list[0], header_list[1]]
        else:
            data_list = [{'x': a, 'y': a} for a, a in zip(data_list1[0], data_list1[0])]
            return [data_list, header_list[0], header_list[0]]
