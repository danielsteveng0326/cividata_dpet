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
    
    # Nuevas rutas para el Asistente IA
    path('peticion/<str:radicado>/asistente/iniciar/', views.iniciar_asistente_respuesta, name='iniciar_asistente_respuesta'),
    path('peticion/<str:radicado>/asistente/', views.mostrar_asistente_respuesta, name='mostrar_asistente_respuesta'),
    path('peticion/<str:radicado>/asistente/procesar/', views.procesar_respuestas_asistente, name='procesar_respuestas_asistente'),
    path('peticion/<str:radicado>/asistente/historial/', views.historial_asistente, name='historial_asistente'),
    path('peticion/<str:radicado>/asistente/descargar-word/', views.descargar_respuesta_word, name='descargar_respuesta_word'),
]