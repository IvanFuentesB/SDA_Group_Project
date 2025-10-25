# mqtt_publisher.py
# ──────────────────────────────────────────────
# This module handles MQTT publishing so the camera PC
# can send shape data (color, type, position) to the game PC.
# ──────────────────────────────────────────────

import paho.mqtt.client as mqtt
import json

# =========================================================
# HOW TO FIND YOUR GAME PC's IP ADDRESS:
# ---------------------------------------------------------
# 1. On the computer running the game:
#    - Press Win + R → type "cmd" → press Enter.
#    - In the command prompt, type: ipconfig
#    - Look for "IPv4 Address" under your active network.
#      It’ll look like: 192.168.x.x
#
# 2. Replace the line below with that number.
# =========================================================
BROKER_IP = "192.168.x.x"  # <--- Replace this with the game PC's IP!
TOPIC = "cv/shapes"

# =========================================================
# MQTT SETUP
# ---------------------------------------------------------
# You must have a broker running on the game PC.
# The easiest is Mosquitto (https://mosquitto.org/download/)
# Once installed, just run "mosquitto -v" in a terminal
# to start it (keep it running).
# =========================================================
client = mqtt.Client()
try:
    client.connect(BROKER_IP, 1883, 60)
    print(f"✅ Connected to MQTT broker at {BROKER_IP}")
except Exception as e:
    print(f"❌ Failed to connect to MQTT broker at {BROKER_IP}: {e}")

# =========================================================
# FUNCTION: send_shape(shape)
# Sends a shape (color, type, position) as JSON
# =========================================================
def send_shape(shape):
    try:
        data = {
            "color": shape.color,
            "type": shape.shape_type,
            "pos": shape.position
        }
        client.publish(TOPIC, json.dumps(data))
        print(f"📤 Sent via MQTT → {data}")
    except Exception as e:
        print(f"⚠️ MQTT send failed: {e}")
