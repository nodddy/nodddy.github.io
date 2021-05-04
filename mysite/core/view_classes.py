from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views import generic
from django.http import HttpResponseRedirect


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
        try:
            context['parent'] = self.get_object()
        except Http404:
            pass
        context.update({'update_name': self.update_name, 'parent_id': self.parent_id})
        return context

    def get(self, request, *args, **kwargs):
        """
        self.object is the parent input_instance (i.e. Experiment or Sample or Step) of the Paramenter input_instance
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
        return self.render_to_response(self.get_context_data(form_invalid=True, formset=formset))
