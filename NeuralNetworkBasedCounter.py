import time
from MosquittoClient import Mosquitto
import socket
import argparse
import real_time_object_detection
# create the thingsboard mqtt client

#tb = Mosquitto("127.0.0.1", 1883, "v1/devices/me/telemetry", True, "vco8rAPy5SkrgpxGFdWy")
#tb = Mosquitto("127.0.0.1", 1883, "v1/devices/me/telemetry", True, "wv8AF92YYJ0GWJz5vW16")

def bucket_(heatmap):
    bucket = {'zone1': 0, 'zone2': 0, 'zone3': 0, 'zone4':0, 'zone5': 0}
    for face in heatmap:
        (x1, y1, x2, y2) = face
        x = (x1 + x2) / 2
        if 0 < x < 768:
            bucket['zone1'] += 1
        if 769 < x < 1536:
            bucket['zone2'] += 1
        if 1537 < x < 2304:
            bucket['zone3'] += 1
        if 2305 < x < 3072:
            bucket['zone4'] += 1
        if 3073 < x < 3840:
            bucket['zone5'] += 1
    return bucket
            
        

hostname = str(socket.gethostname())
hostname = hostname.replace('.local', '')
#hostname = "Top Gun"
db = Mosquitto("192.168.20.190", 8883, "v1/peoplecount/%s" % hostname, False)

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", default="MobileNetSSD_deploy.prototxt",
    help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", default="1066x300_dsv3c_1250ap.caffemodel",
    help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
    help="minimum probability to filter weak detections")
ap.add_argument("-n", "--camera", type=str, default=0,
        help="camera number")
ap.add_argument("-w", "--width", type=int, default=3840,
        help="camera capture width")
ap.add_argument("-t", "--height", type=int, default=1080,
        help="camera capture height")
ap.add_argument("-r", "--cnn_resolution", type=str, default="1066x300",
        help="resolution at which the cnn was trained on")
args = vars(ap.parse_args())

pc = real_time_object_detection.PeopleCounter(args)


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
        count, heatmap = pc.getPeopleCount()
        bucket = bucket_(heatmap)
        print(bucket)
        #inUse = int(pc.isCameraStreaming())
        inUse = 0 
#        tb.publish(count, inUse)
        db.publish(count, inUse, bucket)


