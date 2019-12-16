import time
from MosquittoClient import Mosquitto
import socket
import argparse
import random
import string
# create the thingsboard mqtt client

#tb = Mosquitto("127.0.0.1", 1883, "v1/devices/me/telemetry", True, "vco8rAPy5SkrgpxGFdWy")
#tb = Mosquitto("127.0.0.1", 1883, "v1/devices/me/telemetry", True, "wv8AF92YYJ0GWJz5vW16")

def bucket_():
    bucket = {'zone1': 0, 'zone2': 0, 'zone3': 0, 'zone4':0, 'zone5': 0}
    return bucket
            
        
hostname = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7))
#hostname = "Top Gun"
db = Mosquitto("192.168.20.190", 8883, "v1/peoplecount/%s" % hostname, False)

poll_time = 5
   # for every 5 seconds
   # read the peopleCount API
   # publish to tb and db
start = time.time()
#tb.loop_start()
db.loop_start()
while True:
    #tb.loop(0.5)
    #db.loop(0.5)
    if (time.time() - start) > poll_time:
        start = time.time()
        count = random.randint(0, 10) 
        bucket = bucket_()
        print(bucket)
        #inUse = int(pc.isCameraStreaming())
        inUse = 0 
#        tb.publish(count, inUse)
        db.publish(count, inUse, bucket)


