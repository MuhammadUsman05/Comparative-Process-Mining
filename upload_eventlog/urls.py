from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    path('', views.upload_page, name='upload_page'),
    path('AjaxCall', views.AjaxCall, name='AjaxCall'),
    path('AjaxDownload', views.AjaxDownload, name='AjaxDownload')

]