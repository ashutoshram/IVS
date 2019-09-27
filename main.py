import time
import PeopleCount
from MosquittoClient import Mosquitto
# create the thingsboard mqtt client

tb = Mosquitto("127.0.0.1", 1883, "v1/devices/me/telemetry", True, "vco8rAPy5SkrgpxGFdWy")

db = Mosquitto("127.0.0.1", 8883, "v1/peoplecount", False)

pc = PeopleCount.PeopleCountTester(5, False, -1)


poll_time = 5
   # for every 5 seconds
   # read the peopleCount API
   # publish to tb and db
start = time.time()
while True:
    tb.loop(0.5)
    db.loop(0.5)
    if (time.time() - start) > poll_time:
        start = time.time()
        count = int(pc.getPeopleCount())
        inUse = int(pc.isCameraStreaming())
        tb.publish(count, inUse)
        db.publish(count, inUse)
