from django.contrib import admin
from django.urls import path
from django.urls import include
from rango import views

urlpatterns = [
    path('', views.index, name='index'),
    #any urls starting with rango/ to be handled by rango app.
    path('rango/', include('rango.urls')),
    path('admin/', admin.site.urls),
]
