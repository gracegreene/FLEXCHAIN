"""FlexChainDjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from flexchain.views import home, product, vendor, task, event

urlpatterns = [
    path('admin/', admin.site.urls, name="admin"),
    path('', home, name="home"),
    path('product/', product, name="product"),
    path('vendor/', vendor, name="vendor"),
    path('task/', task, name="task"),
    path('event/', event, name="event"),
    re_path(r'^__django_datatables__/', include('django_datatables.urls')),
]
