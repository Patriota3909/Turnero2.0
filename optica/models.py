from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class EstadoTurno(models.TextChoices):
    EN_ESPERA = 'En espera', 'En espera'
    LLAMANDO = 'Llamando', 'Llamando'
    ATENDIENDO = 'Atendiendo', 'Atendiendo'
    NO_RESPONDIO = 'No respondió', 'No respondió'
    FINALIZADO = 'Finalizado', 'Finalizado'

class Turno(models.Model):
    TIPO_CHOICES = [
        ('K', 'Entrega'),
        ('P', 'Presupuesto'),
    ]
    
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    numero = models.PositiveIntegerField()  # Va de 1 a 200
    estado = models.CharField(
        max_length=20,
        choices=EstadoTurno.choices,
        default=EstadoTurno.EN_ESPERA,
    )
    usuario_asignado = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='turnos'
    )
    creado_en = models.DateTimeField(default=now)
    actualizado_en = models.DateTimeField(auto_now=True)
    hora_inicio_atencion = models.DateTimeField(null=True, blank=True)
    hora_fin_atencion = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['tipo', 'numero'], name='unique_turno')
        ]
        ordering = ['creado_en']

    def __str__(self):
        return f"{self.tipo}{self.numero} ({self.get_estado_display()})"

    @property
    def audio(self):
    
        return f"{self.tipo}{self.numero}.mp3"
