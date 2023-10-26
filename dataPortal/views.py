from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from .forms import CommonDataSearchForm
from .dataPostProcessing import *

def index(request):
    return HttpResponse("Hello world, you're at the data portal index.")


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request=request, template_name='dataPortal/register.html')


def match_search(request):
    form = CommonDataSearchForm()
    if request.method == 'POST':
        form = CommonDataSearchForm(request.POST)
        if form.is_valid():
            teamDataSearch(form)

            '''
            ricerca dei match e passaggio dei risultati al template come variabili di contesto
            '''
            return render(request=request, template_name='dataPortal/teamDataSearch.html', context={'form': form, 'matches': matches})
    return render(request, 'dataPortal/teamDataSearch.html', {'form': form})

