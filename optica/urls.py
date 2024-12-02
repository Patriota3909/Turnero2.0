from django.urls import path
from . import views
urlpatterns = [
    path('', views.layout, name='home'),
    path('logout/', views.exit, name='exit'),
    path('turnos/', views.turnos, name ="turnos"),
    path('crear-turno/', views.crear_turno, name='crear_turno'),
    path('llamar-siguiente/', views.llamar_siguiente_turno, name='llamar_siguiente'),
]
