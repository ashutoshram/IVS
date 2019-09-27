import PeopleCount
import paho.mqtt.client as mqtt
import socket
import sys
import traceback
import json
import threading
import time


class Mosquitto():
    def __init__(self, IP, port, topic_, thingsboard, accesstoken=""):
        try:
            self.hostname = str(socket.gethostname())
            self.hostname = self.hostname.replace('.local', '')
            self.IP = IP
            self.port = port
            self.topic = topic_
            self.poll_time = 5
            self.client = mqtt.Client("PClient", userdata=self, protocol=mqtt.MQTTv31)
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.on_log = self.on_log
            if thingsboard:
                self.client.username_pw_set(accesstoken, "")
            self.client.connect(IP, port)
            self.connection = True
        except:
            print("Could not connect to Thingsboard, Postgresql or PeopleCountTester")
            traceback.print_exc()
            self.connection = False
            t = threading.Thread(target=self.try_reconnect(), args=())
            t.start()
    
    def on_disconnect(self, client, userdata, flags, rc, *extra_params):
        self.try_reconnect()
    
    def on_connect(self, client, userdata, flags, rc, *extra_params):
        return_codes = {
            0:"Connection Successful",
            1:"Connection Refused: Incorrect Protocol Version",
            2:"Connection Refused: Invalid Client Identifier",
            3:"Connection Refused: Server Unavailable",
            4:"Connection Refused: Bad Username Or Password",
            5:"Connection Refused: Not Authorized"}
        error_str = return_codes[int(rc)]  if rc >= 0 or rc <= 5 else "Unknown Error"
        print("Connection returned " + error_str)
    
    def on_log(self, client, userdata, level, buf):
        print("log: ",buf)
    
    def publish(self, count, inUse):
        if self.connection is False:
            return
        print('count = %d, inUse = %d' % (count, inUse))
        d = {"hostname": self.hostname, "peopleCount" : count, "cameraInUse" : inUse,}
        self.client.publish(self.topic, json.dumps(d)) #publish
    
    
    def on_message(self, client, userdata, msg):
        data = json.loads(msg.payload)
        print(data)
    
    def loop(self, timeout_):
        self.client.loop(timeout=timeout_)
    
    def try_reconnect(self):
        while True:
            try:
                self.client.connect(self.IP, self.port)
                self.connection = True
                break
            except:
                traceback.print_exc()
            time.sleep(3)
