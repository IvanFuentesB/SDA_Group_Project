# mqtt_publisher.py
# ──────────────────────────────────────────────
# Handles sending shape data (color, type, position)
# from the camera PC → to the game PC through MQTT.
# ──────────────────────────────────────────────

import paho.mqtt.client as mqtt
import json

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
BROKER_IP = "localhost"  # 👈 replace this with the game PC’s IP
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
    client.connect(BROKER_IP, 1883, 60)
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
