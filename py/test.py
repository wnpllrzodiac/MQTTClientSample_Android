import paho.mqtt.client as mqtt # apt install python3-paho-mqtt
import json
import time
import sys
from threading import Timer

# https://mp.weixin.qq.com/s/4kRsCoaKYS_V7crQPCS3cw?scene=262&from=industrynews#rd
# https://support.huaweicloud.com/usermanual-roma/roma_03_4003.html
# https://juejin.cn/post/7381804958126080052

message_payload = {
    "services": [
        {
            "service_id": "stm32",
            "properties": {
                "MQ135": 60,
                "DHT11_T": 24,
                "DHT11_H": 60,
                "SOIL_H": 50,
                "motor": 1,
                "FLAME": 0,
                "GPS": {
                    "lon": 120.21,
                    "lat": 30.19
                }
            }
        }
    ]
}

def on_connect(client, userdata, flags, reason_code): #, properties):
    global pub_mode
    global SUBSCRIBE_TOPIC2
    print(f"Connected with result code {reason_code}")

    # 连接结果代码（result code）
    # 0: 成功
    # 1: 连接不可用（例如，错误的协议版本或连接不被接受）
    # 2: 标识符被拒绝（通常是客户端ID不唯一）
    # 3: 服务器不可用
    # 4: 用户名或密码错误
    # 5: 未授权

    # 根据rc值判断连接是否成功
    if reason_code == 0:
        print("Connection successful")
        # 在这里可以进行其他初始化操作，比如订阅主题等
        if not pub_mode:
            client.subscribe(PUBLISH_TOPIC)
            print('subscribe: ' + PUBLISH_TOPIC)
    else:
        print("Connection failed")

def on_message(client, userdata, message):
    print(f"Received message from topic '{message.topic}': {message.payload.decode()}")

def publish_message():
    res = client.publish(topic=PUBLISH_TOPIC, payload=json.dumps(message_payload))
    print(res)
    print(f"Published message: {json.dumps(message_payload)}")
    # 设置定时器，以继续定期发布消息
    Timer(PUBLISH_INTERVAL, publish_message).start()

pub_mode = False
if len(sys.argv) > 1 and sys.argv[1] == 'pub':
    pub_mode = True
    print('running in pub mode')
    
MQTT_SERVER = '117.78.5.125'
MQTT_PORT = 1883
CLIENT_ID = '67fcbde85367f573f782aca1_dev1_0_0_2025041506'
USERNAME = '67fcbde85367f573f782aca1_dev1'
PASSWORD = 'aa69017f3c786a9a247dad3befc896b0b56478cc46758b5d4573a4710fadd212'
SUBSCRIBE_TOPIC = "$oc/devices/67fcbde85367f573f782aca1_dev1/sys/messages/down"
SUBSCRIBE_TOPIC2 = "oc/devices/67fcbde85367f573f782aca1_dev1/sys/properties/report"
PUBLISH_TOPIC = "oc/devices/67fcbde85367f573f782aca1_dev1/sys/properties/report"
PUBLISH_INTERVAL = 10

CLIENT_ID_2 = '67fcbde85367f573f782aca1_dev1_0_0_2025042008'
USERNAME_2 = '67fcbde85367f573f782aca1_dev1'
PASSWORD_2 = '17edb4a165a72059e8e205a9ec94c4f26ac2abdeaa75f5c80f32cd77d66a3c6f'

print(f'CLIENT_ID: {CLIENT_ID}')
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1, client_id=CLIENT_ID)
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(USERNAME, PASSWORD)
client.connect(MQTT_SERVER, MQTT_PORT)
if not pub_mode:
    client.loop_forever()

    #client.publish(topic, json_payload, qos=1)
else:
    # 启动网络循环
    client.loop_start()

    # 启动定时发布消息
    publish_message()

    # 主线程保持运行状态
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Disconnecting from MQTT server...")
        client.loop_stop()
        client.disconnect()