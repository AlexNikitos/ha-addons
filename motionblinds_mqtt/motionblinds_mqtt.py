import paho.mqtt.client as mqtt
import json
import time
from motionblinds import MotionGateway

# Читаем параметры из файла, созданного Home Assistant
print("📦 DEBUG: читаем /data/options.json")
with open("/data/options.json", "r") as f:
    options = json.load(f)

print("📄 Содержимое options.json:")
print(json.dumps(options, indent=2))

# Настройки MQTT
MQTT_BROKER = options["mqtt_broker"]
MQTT_PORT = options["mqtt_port"]
MQTT_USER = options["mqtt_user"]
MQTT_PASSWORD = options["mqtt_password"]
MQTT_TOPIC_STATE = options["mqtt_topic_state"]
MQTT_TOPIC_COMMAND = options["mqtt_topic_command"]

# 🔹 MotionBlinds настройки
API_KEY = options["api_key"]
BLINDS = options["blinds"]

#    
print(" Connecting to MotionBlinds...")
motion_blinds = {}

for blind in BLINDS:
    ip = blind["ip"]
    mac = blind["mac"]
    try:
        gateway = MotionGateway(ip=ip, key=API_KEY)
        print(f" Testing {ip} ({mac})")
        gateway.GetDeviceList()
        gateway.Update()
        if mac in gateway.device_list:
            motion_blinds[mac] = gateway.device_list[mac]
            print(f" Connected to blind {mac} at {ip}")
        else:
            print(f" Blind {mac} not found on gateway {ip}")
    except Exception as e:
        print(f" Failed to connect to {mac} at {ip}: {e}")

if not motion_blinds:
    print(" No blinds found! Exiting.")
    exit(1)

print(" All blinds connected!")

#    MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(" Connected to MQTT Broker")
        client.subscribe(MQTT_TOPIC_COMMAND)          #     set
        client.subscribe("home/motionblinds/+/set")   #      MAC
    else:
        print(f" MQTT connection failed with code {rc}")

#        MQTT
last_positions = {}

def update_blind_status():
    """       MQTT """
    for mac, blind in motion_blinds.items():
        try:
            last_position = last_positions.get(mac)
            blind.Update_from_cache()
            position = blind.position or 0  #   None
            moving = last_position is not None and last_position != position  # ,   
            last_positions[mac] = position  #   

            state = {
                "mac": mac,
                "position": position,
                "angle": blind.angle,
                "battery": blind.battery_level,
                "charging": blind.is_charging,
                "moving": moving,  #   
                "last_position": last_position if last_position is not None else position  #   None
            }
            mqtt_client.publish(MQTT_TOPIC_STATE.format(mac), json.dumps(state), retain=True)
            print(f" Publishing to MQTT: {state}")

        except Exception as e:
            print(f" Failed to update blind {mac}: {e}")

#      MQTT
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        topic_parts = msg.topic.split("/")
        mac_from_topic = topic_parts[2] if len(topic_parts) > 3 else None

        #   OPEN, CLOSE, STOP
        if payload in ["OPEN", "CLOSE", "STOP"]:
            for mac, blind in motion_blinds.items():
                if mac_from_topic and mac != mac_from_topic:
                    continue
                if payload == "OPEN":
                    print(f" Opening blinds {mac}")
                    blind.Set_position(100)
                elif payload == "CLOSE":
                    print(f" Closing blinds {mac}")
                    blind.Set_position(0)
                elif payload == "STOP":
                    print(f" Stopping blinds {mac}")
                    blind.Stop()
        else:
            #   JSON,     /
            data = json.loads(payload)
            mac = data.get("mac", mac_from_topic)
            command = data.get("command")
            position = data.get("position")
            angle = data.get("angle")

            if mac in motion_blinds:
                blind = motion_blinds[mac]

                if command == "stop":
                    print(f" Stopping blind {mac} (from JSON)")
                    blind.Stop()

                if command == "open":
                    print(f"Opening blind {mac} (from JSON)")
                    blind.Open()

                if command == "close":
                    print(f"Closing blind {mac} (from JSON)")
                    blind.Close()

                if position is not None:
                    print(f" Setting blind {mac} position to {position}%")
                    blind.Set_position(position)
                    time.sleep(1)

                if angle is not None:
                    print(f" Setting blind {mac} tilt angle to {angle}")
                    blind.Set_angle(angle)
                    time.sleep(1)

        #   
        update_blind_status()

    except Exception as e:
        print(f" Error processing message: {e}")

#   MQTT
mqtt_client = mqtt.Client(protocol=mqtt.MQTTv311)
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)

#      
mqtt_client.loop_start()

while True:
    update_blind_status()
    time.sleep(1)  #      

