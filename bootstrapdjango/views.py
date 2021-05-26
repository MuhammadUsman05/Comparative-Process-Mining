from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def initial(request):
    return render(request,'initial.html')


def anonymization_main(request):
    return render(request, 'initial.html')


def analyses_main(request):
    return render(request, 'initial.html')

def comming_main(request):
    return render(request, 'initial.html')