FROM python:3.11-slim

RUN pip install --no-cache-dir motionblinds paho-mqtt

COPY motionblinds_mqtt.py /app/motionblinds_mqtt.py
COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/run.sh"]
