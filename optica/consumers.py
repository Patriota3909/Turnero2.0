from channels.generic.websocket import AsyncJsonWebsocketConsumer
import logging
logger = logging.getLogger(__name__)


class TurnoConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        #Conectamos al grupo de websockets
        await self.channel_layer.group_add("turnos", self.channel_name)
        await self.accept()
        logger.info(f"WebSocket conectado: {self.channel_name}")
        
    async def disconnect(self, close_code):
        #desconecatart al grupo
        await self.channel_layer.group_discard("turnos", self.channel_name)
        logger.info(f"WebSocket desconectado: {self.channel_name}")
        
        
    async def send_turno_update(self, event):
        logger.info(f"Mensaje enviado: {event['message']}")
        await self.send_json(event["message"]) 
