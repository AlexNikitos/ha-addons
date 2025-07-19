FROM python:3.11-slim

# Устанавливаем необходимые библиотеки
RUN pip install --no-cache-dir motionblinds paho-mqtt

# Копируем скрипт и исполняемый файл
COPY motionblinds_mqtt.py /app/motionblinds_mqtt.py
COPY run.sh /run.sh

# Даём права на выполнение
RUN chmod +x /run.sh

# Указываем точку входа
CMD ["/run.sh"]
