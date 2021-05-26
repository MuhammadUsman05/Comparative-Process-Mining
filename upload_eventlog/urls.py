from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    path('', views.upload_page, name='upload_page')

]