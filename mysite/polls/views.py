from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.views import generic, View
from django.http import HttpResponseRedirect
from django.forms.models import inlineformset_factory
from django.core.files.storage import FileSystemStorage
from django.urls import reverse_lazy
import re, urllib
from fpdf import FPDF
import pandas as pd
import numpy as np
import pdfkit
import json

from .models import Experiment, Sample, File
from .forms import ExperimentForm, FileUploadForm


def index(request):
    """
    First site. Displays all experiments in chronological order. Displays all samples with atleast one associated experiment.
    """
    context = {
        'experiment_list': Experiment.objects.order_by('-date'),
        'sample_list': Sample.objects.exclude(experiments=None)}
    return render(request, 'polls/index.html', context)


class UpdateCreateView(generic.FormView):
    template_name = ''
    model = None
    parent_model = None
    formset = None
    update_name = ''
    fields = {}
    parent_id = int()
    success_url = None

    def dispatch(self, request, formset=None, *args, **kwargs):
        self.update_name = kwargs.get('update_name')
        self.template_name = kwargs.get('template_name')
        self.model = kwargs.get('model')
        self.parent_model = kwargs.get('parent_model')
        self.fields = kwargs.get('fields')
        self.parent_id = kwargs.get('parent_id')
        self.formset = formset
        try:
            self.success_url = self.get_object().get_absolute_url()
        except Http404:
            pass
        return super(UpdateCreateView, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        return get_object_or_404(self.parent_model, id=self.parent_id)

    def get_context_data(self, **kwargs):
        context = super(UpdateCreateView, self).get_context_data(form='', **kwargs)
        context['update_name'] = self.update_name
        context['parent_id'] = self.parent_id
        try:
            context['parent'] = self.get_object()
        except Http404:
            pass
        return context

    def get(self, request, *args, **kwargs):
        """
        self.object is the parent instance (i.e. Experiment or Sample or Step) of the Paramenter instance
        """
        try:
            form = self.formset(instance=self.get_object(), prefix='form')
        except Http404:
            form = self.formset(prefix='form')
        return self.render_to_response(self.get_context_data(formset=form))

    def post(self, request, *args, **kwargs):

        try:
            formset = self.formset(request.POST, request.FILES, instance=self.get_object(), prefix='form')
        except Http404:
            formset = self.formset(request.POST, request.FILES, prefix='form')

        if formset.is_valid():
            return self.form_valid(formset, request)
        else:
            return self.form_invalid(formset)

    def form_valid(self, formset, request=None):
        for form in formset:
            if form.cleaned_data != {}:
                form_instance = form.save(commit=False)
                form_instance.instance = self.get_object()
                form_instance.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, formset):
        return self.render_to_response(self.get_context_data(form_invalid=True,
                                                             formset=formset))


class ExperimentDetailView(generic.DetailView):
    """
    View for the Experiment with all its child models (i.e. Parameter).
    """
    template_name = 'polls/experiment-detail.html'
    object = None

    def get(self, request, *args, **kwargs):
        """
        Takes the parent_id (experiment.id) from url and gets the instance object, which gets returned in context along
        with the instance id (for some reason its also required for proper function)
        """
        self.object = get_object_or_404(Experiment, id=self.kwargs['parent_id'])
        return self.render_to_response(self.get_context_data(parent=self.object,
                                                             parent_id=self.object.id))


class SampleDetailView(generic.DetailView):
    """
    View for the Sample with all its child models (i.e. Parameter) and a link to its experiments.
    """
    template_name = 'polls/sample-detail.html'
    object = None

    def get(self, request, *args, **kwargs):
        """
        Takes the parent_id (experiment.id) from url and gets the instance object, which gets returned in context along
        with the instance id (for some reason its also required for proper function)
        """
        self.object = get_object_or_404(Sample, id=self.kwargs['parent_id'])
        return self.render_to_response(self.get_context_data(parent=self.object,
                                                             parent_id=self.object.id))


class ExperimentUpdateView(UpdateCreateView):
    """
    Updates the experiment instance when a parent_id is given in the url or it creates a new instance.
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
        return inlineformset_factory(self.parent_model,
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
        self.child_formset = inlineformset_factory(self.model,
                                                   self.child_model,
                                                   fields=self.child_fields,
                                                   extra=1,
                                                   can_delete=False)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        step_list = [value for value in self.model.objects.filter(experiment=self.get_object().id).in_bulk().values()]
        child_formset_list = [self.child_formset(instance=child_instance, prefix=f'child_form{index}') for
                              index, child_instance in
                              enumerate(step_list)]
        context['child_formset_list'] = child_formset_list
        return context

    def post(self, request, *args, **kwargs):

        delete_btn_identifier = re.search(r'btn_delete_child-\d+', urllib.parse.urlencode(request.POST))
        if delete_btn_identifier is not None:
            entry = get_object_or_404(self.child_model, id=delete_btn_identifier.group().split('-')[1])
            entry.delete()
            return HttpResponseRedirect(request.path)

        step_list = [value for value in self.model.objects.filter(experiment=self.get_object().id).in_bulk().values()]
        child_formset_list = [self.child_formset(self.request.POST,
                                                 instance=child_instance,
                                                 prefix=f'child_form{index}'
                                                 )
                              for index, child_instance in enumerate(step_list)]

        for child_form in child_formset_list:
            if child_form.is_valid():
                child_form.save()
            else:
                return HttpResponseRedirect(request.path)
        return super().post(request, *args, **kwargs)


class FileView(generic.DetailView):
    template_name = 'polls/file-viewer.html'
    object = None
    file = None
    file_type = ''
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    pdf_config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    pdf_options = {
        'margin-top': '0.1in',
        'margin-right': '0.1in',
        'margin-bottom': '0.1in',
        'margin-left': '0.1in',
        'minimum-font-size': 18,
        'encoding': "UTF-8"
    }

    def get_context_data(self, *args, **kwargs):
        """
        Takes the parent_id (experiment.id) from url and gets the instance object, which gets returned in context along
        with the instance id (for some reason its also required for proper function)
        """
        self.object = get_object_or_404(Experiment, id=self.kwargs['parent_id'])
        self.file = get_object_or_404(File, id=self.kwargs['file_id'])
        self.file_type = self.kwargs['file_type']
        x_header = kwargs.get('x_header')
        y_header = kwargs.get('y_header')
        context = super().get_context_data(**kwargs)

        new_context = {'parent': self.object,
                       'parent_id': self.object.id,
                       'file_name': self.file.name,
                       'file_url': f'{self.file.file.url}.pdf'
                       }

        context.update(new_context)

        if self.file_type == 'csv':
            csv_str = json.loads(self.file.csv)
            if x_header is None or y_header is None:
                if self.file.csv_plot:
                    plot_data = {key: csv_str[key] for key in eval(self.file.csv_plot)}
                else:
                    plot_data = {key: csv_str[key] for key in list(csv_str.keys())[0:2]}
            else:
                plot_data = {key: csv_str[key] for key in [x_header, y_header]}

            context['plot_data'], context['x_label'], context['y_label'] = self.json_to_chart_data(plot_data)
            context['header'] = [k for k in json.loads(self.file.csv).keys()]

            context['plot'] = True
        if self.file_type == 'pdf':
            context['pdf'] = True
        if self.file_type == 'img':
            context['img'] = True

        return context

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.file = get_object_or_404(File, id=self.kwargs['file_id'])
        if 'save_plot' in request.POST.keys():
            self.file.csv_plot = [request.POST['x_select'], request.POST['y_select']]
            self.file.save()
        return self.render_to_response(self.get_context_data(x_header=request.POST['x_select'],
                                                             y_header=request.POST['y_select']))

    @staticmethod
    def json_to_chart_data(json_str):
        header_list = [k for k in json_str.keys()]
        data_list1 = [v.values() for v in json_str.values()]
        if len(header_list) == 2:
            data_list = [{'x': a, 'y': b} for a, b in zip(data_list1[0], data_list1[1])]
            return [data_list, header_list[0], header_list[1]]
        else:
            data_list = [{'x': a, 'y': a} for a, a in zip(data_list1[0], data_list1[0])]
            return [data_list, header_list[0], header_list[0]]
