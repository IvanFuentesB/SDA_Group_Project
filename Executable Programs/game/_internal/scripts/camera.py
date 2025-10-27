import paho.mqtt.client as mqtt
import json
import time
from scripts.shape import Shape, Circle
class Camera:
    def __init__(self, game, host_ip, port, topic = "cv/shapes"):
        self.game = game
        self.host = host_ip
        self.port = port
        self.topic = topic
        self.last_shape = None
        
        self.client = mqtt.Client()
        self.client.on_message = self._on_message
        self.client.connect(self.host, self.port)
        self.client.subscribe(self.topic)
        self.client.loop_start()
        
    def _on_message(self, client, userdata, message):
        try:
            data = json.loads(message.payload.decode())
            self.last_shape = (data["color"], data["type"])
        except (json.JSONDecodeError, KeyError):
            self.last_shape = None
    
    def get_latest_shape(self):
        if self.last_shape is None:
            return None
        color = self.last_shape[0].lower()
        type = None
        if self.last_shape[1] == "Triangle":
            type = "triangle"
        if self.last_shape[1] == "Quadrilateral":
            type = "square"
        if self.last_shape[1] == "Circle":
            type = "circle"
        if type == 'circle':
            return Circle(self.game, color, (0, 0), (16, 16))
        if type == "triangle":
            return Shape(self.game,type,color,(0, 0))
        if type == "square":
            return Shape(self.game, type, color, (0, 0))
        
        
            
        