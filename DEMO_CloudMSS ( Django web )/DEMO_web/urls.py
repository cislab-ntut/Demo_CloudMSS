"""
URL configuration for DEMO_web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path

from my_app import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.main),
    path("MSS_sys/", views.MSS_sys),
    path("recover_secret/", views.recover_secret),
    path("kNN_service/", views.kNN_service),
    path("convert_threshold/", views.convert_threshold),
    path("get_op_record/", views.get_op_record,)
]
