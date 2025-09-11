# peticiones/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('crear/', views.crear_peticion, name='crear_peticion'),
    path('lista/', views.ListaPeticiones.as_view(), name='lista_peticiones'),
    path('peticion/<str:radicado>/', views.detalle_peticion, name='detalle_peticion'),
    path('peticion/<str:radicado>/reprocesar/', views.reprocesar_peticion, name='reprocesar_peticion'),
    path('peticion/<str:radicado>/cambiar-estado/', views.cambiar_estado_peticion, name='cambiar_estado_peticion'),
    path('peticion/<str:radicado>/editar-peticionario/', views.editar_peticionario, name='editar_peticionario'),
    path('peticion/<str:radicado>/datos-peticionario/', views.obtener_datos_peticionario, name='obtener_datos_peticionario'),
]