from django.contrib.auth.decorators import login_required
from channels.layers import get_channel_layer
from django.shortcuts import render, redirect
from asgiref.sync import async_to_sync
from django.contrib.auth import logout
from django.contrib import messages
from .models import Turno
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt


def exit(request):
    logout(request)
    return redirect('home')

@login_required
def layout(request):
    return render(request, 'optica/layout.html')

#Esta vista sirve para visualizar los turnos (pagina de usuarios)---------------
def turnos(request):
    turnos_entrega = Turno.objects.filter(tipo="K", estado='En espera').order_by('numero')
    turnos_presupuesto = Turno.objects.filter(tipo="P", estado="En espera").order_by('numero')
    turnos_llamado = Turno.objects.filter(estado='Llamando').first()
    return render(request, 'optica/turnos.html', {
        'turnos_entrega': turnos_entrega,
        'turnos_presupuesto': turnos_presupuesto,
        'turnos_llamando': turnos_llamado,
    })
    
#Generamos la vista para poder crear turnos
def crear_turno(request):
    if request.method == "POST":
        tipo = request.POST.get('tipo')
        if tipo not in ['K', 'P']:
            messages.error(request, "Tipo de turno invalido")
            return redirect('crear_turno')
        #buscamos el proximo turno disponible
        ultimo_turno = Turno.objects.filter(tipo=tipo).order_by("-numero").first()
        siguiente_numero = (ultimo_turno.numero + 1 ) if ultimo_turno else 1
        
        #Validamos que no exceda el limite (200)
        if siguiente_numero > 200:
            messages.error(request, "No se pueden generar mas turnos")
            return redirect('crear_turno')
        
        #Crear turno como tal
        turno = Turno.objects.create(tipo=tipo, numero=siguiente_numero, estado="En espera")
        messages.success(request, f"Turno{tipo}{siguiente_numero} generado correctamente")
        
        #Aqui notificamos a los clientes conectados 
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "turnos",
            {
                "type": "send_turno_update",
                "message":{
                    "id": turno.id,
                    "tipo": turno.tipo,
                    "numero": turno.numero,
                    "estado": turno.get_estado_display(),
                },
            },
        )
        return redirect('crear_turno') #redirige para mostrar el modal
    
    return render(request, 'optica/crear_turno.html') 
    
    
#vamos a generar la vista para hacer el cambio del estatus a "llamando"
@csrf_exempt
def llamar_siguiente_turno(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        tipo = body.get('tipo')  # Tipo de turno: "K" o "P"

        # Validar tipo de turno
        if tipo not in ['K', 'P']:
            return JsonResponse({'error': 'Tipo de turno inválido.'}, status=400)

        # Obtener el siguiente turno en espera para el tipo seleccionado
        siguiente_turno = Turno.objects.filter(tipo=tipo, estado='En espera').order_by('numero').first()
        if not siguiente_turno:
            return JsonResponse({'error': f'No hay turnos en espera para {tipo}.'}, status=404)

        # Asignar el turno al usuario y cambiar el estado
        siguiente_turno.estado = 'Llamando'
        siguiente_turno.usuario_asignado = request.user
        siguiente_turno.save()

        # Notificar a todos los clientes conectados
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "turnos",  # Nombre del grupo
            {
                "type": "send_turno_update",
                "message": {
                    "id": siguiente_turno.id,
                    "tipo": siguiente_turno.tipo,
                    "numero": siguiente_turno.numero,
                    "estado": siguiente_turno.get_estado_display(),
                    "usuario": siguiente_turno.usuario_asignado.username,
                },
            },
        )

        # Devolver información del turno al cliente que lo llamó
        return JsonResponse({
            'id': siguiente_turno.id,
            'tipo': siguiente_turno.tipo,
            'numero': siguiente_turno.numero,
            'estado': siguiente_turno.get_estado_display(),
        })

    return JsonResponse({'error': 'Método no permitido.'}, status=405)