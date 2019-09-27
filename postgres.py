from pg import DB
import paho.mqtt.client as mqtt
import json
import time

def on_log(client, userdata, level, buf):
    print("log: ",buf)

def on_connect(client, userdata, flags, rc, *extra_params):
    return_codes = {
     0:"Connection Successful",
     1:"Connection Refused: Incorrect Protocol Version",
     2:"Connection Refused: Invalid Client Identifier",
     3:"Connection Refused: Server Unavailable",
     4:"Connection Refused: Bad Username Or Password",
     5:"Connection Refused: Not Authorized"}
    error_str = return_codes[int(rc)]  if rc >= 0 or rc <= 5 else "Unknown Error"
    print("Connection returned " + error_str)

def on_message(client, userdata, msg):
    # userdata in our case will be an instance of testPeopleCount.PeopleCountTester
    print('Topic: ' + msg.topic + '\nMessage: ' + str(msg.payload))
    # Decode JSON request
    storeMessage(msg)
    # Check request method

#def peopleCount(msg):
#    data = json.loads(msg.payload)

db = DB(dbname='jabra', host='127.0.0.1', port=5432, user="", passwd="")

def storeMessage(msg):
    global db
    message = json.loads(msg.payload)
    peopleCount = int(message['peopleCount'])
    roomID = message['hostname']
    busyStatus = int(message['cameraInUse'])
    db.insert('telemetry', roomid=roomID, peoplecount=peopleCount, busystatus=busyStatus)    
    

    

if __name__ == '__main__':

    broker_ip = "127.0.0.1"
    broker_port = 8883
    client = mqtt.Client("Python", protocol=mqtt.MQTTv31) #create new instance
    client.on_connect = on_connect
    client.on_log = on_log
    client.on_message = on_message
    client.connect(broker_ip, broker_port) #connect to broker
    client.loop_start()
    client.subscribe("v1/peoplecount")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        client.loop_stop()
        print("exit")


