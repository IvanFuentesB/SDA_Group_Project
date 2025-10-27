# mqtt_publisher.py
# ──────────────────────────────────────────────
# Handles sending shape data (color, type, position)
# from the camera PC → to the game PC through MQTT.
# ──────────────────────────────────────────────

import paho.mqtt.client as mqtt
import json
import os
# =========================================================
# HOW TO GET THE GAME PC’s IP:
# ---------------------------------------------------------
# 1. On the computer running the game:
#    - Hit Win + R → type “cmd” → press Enter
#    - In the terminal, type: ipconfig
#    - Scroll until you see “IPv4 Address” under your network
#      (should look like 192.168.x.x)
#
# 2. Replace the IP below with that number.
# =========================================================

with open('config.txt', 'r') as f:
            config = dict(
                line.strip().split('=')
                for line in f
                if line.strip() and not line.startswith('#')
            )
mqtt_ip = config.get('mqtt_ip')
mqtt_port = int(config.get('mqtt_port', '1883'))
BROKER_IP = mqtt_ip  # 👈 replace this with the game PC’s IP
TOPIC = "cv/shapes"

# =========================================================
# MQTT SETUP
# ---------------------------------------------------------
# The game PC needs to have Mosquitto running as the broker.
# If you haven’t already:
#   - Install it (https://mosquitto.org/download/)
#   - Then open CMD and run: mosquitto -v
#   - Leave that window open while everything runs
# =========================================================
client = mqtt.Client()
try:
    client.connect(BROKER_IP, int(mqtt_port), 60)
    print(f"✅ Connected to MQTT broker at {BROKER_IP}")
except Exception as e:
    print(f"❌ Couldn’t connect to MQTT broker at {BROKER_IP}: {e}")

# =========================================================
# send_shape(shape)
# ---------------------------------------------------------
# Sends a shape (color/type/pos) as a JSON message
# over MQTT to the game PC.
# =========================================================
def send_shape(shape):
    try:
        data = {
            "color": shape.color,
            "type": shape.shape_type,
            "pos": shape.position
        }
        client.publish(TOPIC, json.dumps(data))
        print(f"📤 Sent shape → {data}")
    except Exception as e:
        print(f"⚠️ MQTT send failed: {e}")
