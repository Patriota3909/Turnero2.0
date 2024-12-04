from django.core.management.base import BaseCommand
from optica.models import Turno

class Command(BaseCommand):
    help = 'Reinicia los turnos diarios'

    def handle(self, *args, **kwargs):
        #restablecemos los turnos
        Turno.objects.all().update(estado ="En espera", usuario_asignado=None, hora_inicio_atencion=None, hora_fin_atencion=None)
        self.stdout.write(self.style.SUCCESS("Turnos reiniciados con exito"))