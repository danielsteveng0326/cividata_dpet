from django.urls import path
from . import views
from . import auth_views

urlpatterns = [
    # Autenticación
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('cambiar-contrasena/', auth_views.cambiar_contrasena, name='cambiar_contrasena'),
    path('recuperar-contrasena/', auth_views.recuperar_contrasena, name='recuperar_contrasena'),
    path('reset-password/<uidb64>/<token>/', auth_views.reset_contrasena, name='reset_contrasena'),
    
    # Gestión de Usuarios (solo administradores)
    path('usuarios/', auth_views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/registro/', auth_views.registro_usuario, name='registro_usuario'),
    
    # Gestión de Dependencias (solo administradores)
    path('dependencias/', auth_views.lista_dependencias, name='lista_dependencias'),
    path('dependencias/crear/', auth_views.crear_dependencia, name='crear_dependencia'),
    
    # Gestión de Días No Hábiles (solo administradores)
    path('calendario-dias-no-habiles/', auth_views.calendario_dias_no_habiles, name='calendario_dias_no_habiles'),
    path('agregar-dia-no-habil/', auth_views.agregar_dia_no_habil, name='agregar_dia_no_habil'),
    path('eliminar-dia-no-habil/<int:dia_id>/', auth_views.eliminar_dia_no_habil, name='eliminar_dia_no_habil'),
    path('verificar-dia-habil/', auth_views.verificar_dia_habil, name='verificar_dia_habil'),
    path('verificar-dias-mes/', auth_views.obtener_dias_no_habiles_mes, name='obtener_dias_no_habiles_mes'),
    
    # Peticiones
    path('', views.index, name='index'),
    path('crear/', views.crear_peticion, name='crear_peticion'),
    path('lista/', views.ListaPeticiones.as_view(), name='lista_peticiones'),
    path('peticion/<str:radicado>/', views.detalle_peticion, name='detalle_peticion'),
    path('peticion/<str:radicado>/reprocesar/', views.reprocesar_peticion, name='reprocesar_peticion'),
    path('peticion/<str:radicado>/cambiar-estado/', views.cambiar_estado_peticion, name='cambiar_estado_peticion'),
    path('peticion/<str:radicado>/editar-peticionario/', views.editar_peticionario, name='editar_peticionario'),
    path('peticion/<str:radicado>/datos-peticionario/', views.obtener_datos_peticionario, name='obtener_datos_peticionario'),
    
    # Asistente IA
    path('peticion/<str:radicado>/asistente/iniciar/', views.iniciar_asistente_respuesta, name='iniciar_asistente_respuesta'),
    path('peticion/<str:radicado>/asistente/', views.mostrar_asistente_respuesta, name='mostrar_asistente_respuesta'),
    path('peticion/<str:radicado>/asistente/procesar/', views.procesar_respuestas_asistente, name='procesar_respuestas_asistente'),
    path('peticion/<str:radicado>/asistente/historial/', views.historial_asistente, name='historial_asistente'),
    path('peticion/<str:radicado>/asistente/descargar-word/', views.descargar_respuesta_word, name='descargar_respuesta_word'),
]