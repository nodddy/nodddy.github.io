from django.http import HttpResponse, HttpResponseRedirect
from .models import Experiment
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_experiment_list'

    def get_queryset(self):
        """Return experiments based on latest by time"""
        return Experiment.objects.order_by('-date')


class DetailView(generic.DetailView):
    model = Experiment
    template_name = 'polls/detail.html'
    context_object_name = 'parameter_list'

    def get_queryset(self):
        """Return list of Parameters"""

        return Parameter.objects


# def detail(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/detail.html', {'question': question})


def detail(request, experiment_id):
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    return render(request, 'polls/detail.html', {'experiment': experiment})
    return HttpResponseRedirect(reverse('polls:detail', args=(experiment_id,)))

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': 'You didnt select a choice.',
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfullyn dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
    return HttpResponseRedirect(reverse('polls:results', args=(question_id,)))
