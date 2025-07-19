#!/bin/sh

echo "🔧 Генерация options.json из переменных окружения..."

# Записываем параметры из переменных окружения в options.json
cat <<EOF > /data/options.json
{
  "mqtt_broker": "$MQTT_BROKER",
  "mqtt_port": $MQTT_PORT,
  "mqtt_user": "$MQTT_USER",
  "mqtt_password": "$MQTT_PASSWORD",
  "mqtt_topic_state": "$MQTT_TOPIC_STATE",
  "mqtt_topic_command": "$MQTT_TOPIC_COMMAND",
  "api_key": "$API_KEY",
  "blinds": $BLINDS
}
EOF

echo "🚀 Запускаем motionblinds_mqtt.py..."
python3 /app/motionblinds_mqtt.py
