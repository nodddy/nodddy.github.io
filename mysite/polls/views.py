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

    def get(self, request, *args, **kwargs):
        """
        Takes the parent_id (experiment.id) from url and gets the instance object, which gets returned in context along
        with the instance id (for some reason its also required for proper function)
        """
        self.object = get_object_or_404(Experiment, id=self.kwargs['parent_id'])
        self.file = get_object_or_404(File, id=self.kwargs['file_id'])
        new_context = {'parent': self.object,
                       'parent_id': self.object.id,
                       'file_name': self.file.name,
                       'file_url': self.file.file.url
                       }
        context = self.get_context_data()
        context.update(new_context)

        if self.file.pdf:
            context['pdf'] = True
            context['file_url'] = self.file.pdf.url

        elif self.file.type == 'pdf':
            self.file.pdf.name = self.file.file.path
            context['pdf'] = True

        elif self.file.type == 'csv':
            df = pd.read_csv(self.file.file.path, delimiter=self.file.file_delimiter)
            self.file.csv = df.to_json()

            self.file.pdf.name = self.csv_to_pdf(self.file)

            context['file_url'] = self.file.pdf.url
            context['pdf'] = True

        elif self.file.type == 'txt':
            try:
                self.file.pdf.name = self.txt_to_pdf(self.file)
            except UnicodeDecodeError:
                print('PDF conversion not possible: UnicodeDecodeError')
                context['file_error_msg'] = f'File conversion no possible. Possibly wrong file type'
                return self.render_to_response(context)
            context['file_url'] = self.file.pdf.url
            context['pdf'] = True

        else:
            context['pdf'] = False
        return self.render_to_response(context)

    def txt_to_pdf(self, file_instance):
        """
        Takes file_instance and generates a pdf file from the txt file, then saves it to the file_instance's
        path with .pdf added.
        :param file_instance: the instance of file model
        :return: A string with the pdf file path
        """
        output_path = f'{self.file.file.path}.pdf'
        pdfkit.from_file(file_instance.file.path, output_path, configuration=self.pdf_config, options=self.pdf_options)
        return output_path

    def csv_to_pdf(self, file_instance):
        """
        Gets the csv attribute from file model and then converts it in form of a JSON string
        to a pandas df and then html with specified CSS in 'pd_options.
        Finally the html gets converted to pdf and saved to the file_instance path with .pdf added.
        :param file_instance: the instance of file model
        :return: A string with the pdf file path
        """
        pd_options = '<html>' \
                     '<meta charset="utf-8">' \
                     '<meta name="viewport" content="width=device-width, initial-scale=1">' \
                     '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/css/bootstrap.min.css"' \
                     ' rel="stylesheet"integrity="sha384-eOJMYsd53ii+scO/bJGFsiCZc+5NDVN2yr8+0RDqr0Ql0h+rP48ckxlpbzKgwra6"' \
                     ' crossorigin="anonymous">' \
                     '<body> {table} </body>' \
                     '</html>'  # bootstrap CSS is loaded from website

        csv = file_instance.csv
        pd.set_option('colheader_justify', 'center')
        df_html = pd_options.format(table=pd.read_json(csv).to_html(na_rep='', classes='table'))
        output_path = f'{file_instance.file.path}.pdf'
        pdfkit.from_string(df_html, output_path, configuration=self.pdf_config, options=self.pdf_options)
        return output_path
