# import the necessary packages
"""
For P3 cameras:
    python3 real_time_object_detection.py -n 1 \
            -w 3840 -t 1080  -r "1200x300" \
            -p P3_mobilenetSSD_deploy.prototxt \
            -m P3_mobilenetSSD_deploy.caffemodel -c 0.3
"""
import numpy as np
import argparse
import imutils
import time
import cv2
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", default="MobileNetSSD_deploy.prototxt.txt",
	help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", default="MobileNetSSD_deploy.caffemodel",
	help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
	help="minimum probability to filter weak detections")
ap.add_argument("-n", "--camera", type=str, default="0",
        help="camera number")
ap.add_argument("-w", "--width", type=int, default=3840,
        help="camera capture width")
ap.add_argument("-t", "--height", type=int, default=1080,
        help="camera capture height")
ap.add_argument("-r", "--cnn_resolution", type=str, default="1066x300",
        help="resolution at which the cnn was trained on")
args = vars(ap.parse_args())

# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class

class PeopleCounter:
    def __init__(self, args):
        self.net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])
        self.cam = args["camera"]
    
    def getPeopleCount(self):
        self.cap = cv2.VideoCapture(self.cam)
        CLASSES = ["background",  "head", "body", "wb"]
        COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
        HeatMap = []
        try:
            (cnnInputWidth, cnnInputHeight) = tuple(map(int, args["cnn_resolution"].split('x')))
            print("Parsed CNN input resolution as (%d, %d)" % (cnnInputWidth, cnnInputHeight))
        except:
            print('Caught an exception parsing %s' % args["cnn_resolution"])
            sys.exit(1)

        for i in range(30):
            # flushing out bad frames
            ret, frame = self.cap.read()
        if ret:
            (h, w, c) = frame.shape
            adjustAspect = True
            if adjustAspect:
                resized = np.zeros((cnnInputHeight, cnnInputWidth, c), dtype=np.uint8)
                resized[0:cnnInputHeight, 0:int(cnnInputWidth/2)] = cv2.resize(frame, (int(cnnInputWidth/2), cnnInputHeight))
            else:
                resized = cv2.resize(frame, (cnnInputWidth, cnnInputHeight))
            blob = cv2.dnn.blobFromImage(resized, 0.007843, (cnnInputWidth, cnnInputHeight), 127.5)

            # pass the blob through the network and obtain the detections and
            # predictions
            self.net.setInput(blob)
            detections = self.net.forward()
            # loop over the detections
            detected = 0
            peopleCount = 0
            for i in np.arange(0, detections.shape[2]):
                # extract the confidence (i.e., probability) associated with
                # the prediction
                idx = int(detections[0, 0, i, 1])
                confidence = detections[0, 0, i, 2]

                # filter out weak detections by ensuring the `confidence` is
                # greater than the minimum confidence
                if confidence > args["confidence"] and idx < len(CLASSES) and idx >= 0:
                    # extract the index of the class label from the
                    # `detections`, then compute the (x, y)-coordinates of
                    # the bounding box for the object
                    scale_box = np.array([w, h, w, h])
                    if adjustAspect: scale_box = np.array([w*2, h, w*2, h])
                    box = detections[0, 0, i, 3:7] * scale_box
                    (startX, startY, endX, endY) = box.astype("int")
                    faces = (startX, startY, endX, endY) 

                    # draw the prediction on the frame
                    label = "{}: {:.2f}%".format(CLASSES[idx],
                                                 confidence * 100)
                    cv2.rectangle(frame, (startX, startY), (endX, endY),
                                  COLORS[idx], 2)
                    y = startY - 15 if startY - 15 > 15 else startY + 15
                    cv2.putText(frame, label, (startX, y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
                    detected = 1
                    if CLASSES[idx] == "head":
                        HeatMap.append(faces)
                        peopleCount += 1
            print("RETURNING PEOPLECOUNT")
            self.cap.release()
            return peopleCount, HeatMap
        else:
            return 0

            

def PeopleCount(args):
    CLASSES = ["background",  "head", "body", "wb"]
    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

    # load our serialized model from disk
    print("[INFO] loading model...")
    net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

    img = None
    cam = args["camera"]
    width = args["width"]
    height = args["height"]
    try:
        cam = int(cam)
        print('Using camera %d' % cam)
    except:
        img = cv2.imread(cam)
        if img is not None:
            width = img.shape[1]
            height = img.shape[0]
            print('input %s is of shape %s' % (cam, repr(img.shape[:2])))
        else:
            print('input could be a video')



    # initialize the video stream, allow the cammera sensor to warmup,
    # and initialize the FPS counter
    print("[INFO] starting video stream...")
    cap = None
    if img is None:
        cap = cv2.VideoCapture(cam)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        print('Capturing with resolution %d,%d' % (height, width))

    fcount = 0
    fcount_det = 0
    start = time.time()

    try:
        (cnnInputWidth, cnnInputHeight) = tuple(map(int, args["cnn_resolution"].split('x')))
        print("Parsed CNN input resolution as (%d, %d)" % (cnnInputWidth, cnnInputHeight))
    except:
        print('Caught an exception parsing %s' % args["cnn_resolution"])
        sys.exit(1)

    P3 = False
    if args["model"].startswith("P3"):
        P3 = True
        CLASSES = ["unknown", "head", "person", "whiteboard"]

    adjustAspect = False
    aspect = width / height
    if P3:
        if aspect != (3840/1080) and aspect != (3840/1088):
            adjustAspect = True
    # loop over the frames from the video stream
    while True:
        try:
            # grab the frame from the threaded video stream and resize it
            # to have a maximum width of 400 pixels
            if img is None:
                ret, frame = cap.read()
                if ret < 0 or frame is None:
                    print('Unable to read from camera')
                    break
                if frame.shape[:2] != (height, width):
                    print('Unable to read %d,%d from the camera; read %s' % (height, width, repr(frame.shape[:2])))
                    break
            else:
                frame = img.copy()

            # grab the frame dimensions and convert it to a blob
            (h, w, c) = frame.shape
            if adjustAspect:
                resized = np.zeros((cnnInputHeight, cnnInputWidth, c), dtype=np.uint8)
                resized[0:cnnInputHeight, 0:int(cnnInputWidth/2)] = cv2.resize(frame, (int(cnnInputWidth/2), cnnInputHeight))
            else:
                resized = cv2.resize(frame, (cnnInputWidth, cnnInputHeight))
            blob = cv2.dnn.blobFromImage(resized, 0.007843, (cnnInputWidth, cnnInputHeight), 127.5)

            # pass the blob through the network and obtain the detections and
            # predictions
            net.setInput(blob)
            detections = net.forward()
            # loop over the detections
            detected = 0
            peopleCount = 0
            for i in np.arange(0, detections.shape[2]):
                # extract the confidence (i.e., probability) associated with
                # the prediction
                idx = int(detections[0, 0, i, 1])
                confidence = detections[0, 0, i, 2]

                # filter out weak detections by ensuring the `confidence` is
                # greater than the minimum confidence
                if confidence > args["confidence"] and idx < len(CLASSES) and idx >= 0:
                    # extract the index of the class label from the
                    # `detections`, then compute the (x, y)-coordinates of
                    # the bounding box for the object
                    scale_box = np.array([w, h, w, h])
                    if adjustAspect: scale_box = np.array([w*2, h, w*2, h])
                    box = detections[0, 0, i, 3:7] * scale_box
                    (startX, startY, endX, endY) = box.astype("int")

                    # draw the prediction on the frame
                    label = "{}: {:.2f}%".format(CLASSES[idx],
                                                 confidence * 100)
                    cv2.rectangle(frame, (startX, startY), (endX, endY),
                                  COLORS[idx], 2)
                    y = startY - 15 if startY - 15 > 15 else startY + 15
                    cv2.putText(frame, label, (startX, y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
                    detected = 1
                    if CLASSES[idx] == "head":
                        peopleCount += 1
                    if img is not None:
                        if CLASSES[idx] == "whiteboard":
                            wb = frame[startY:endY, startX:endX]
                            cv2.imshow('wb', wb)

            fcount_det += detected;
            print(peopleCount)

            # show the output frame
            #cv2.imshow("Frame", frame)
            key = cv2.waitKey(2) & 0xFF
            

            # if the `q` key was pressed, break from the loop
            if key == ord('q') or key == 27:
                break

            # update the FPS counter
            #fps.update()
            fcount += 1
            if time.time() - start > 3.0:
                #print('elapsed time = %f, fcount = %d' % (time.time() - start, fcount))
                #print('fcount = %d, fcount_det = %d' % (fcount, fcount_det))
                print('fps = ', fcount / (time.time() - start))
                start = time.time()
                fcount = 0
                fcount_det = 0
        except KeyboardInterrupt:
            break

    cv2.destroyAllWindows()
    if cap is not None: cap.release()


if __name__ == "__main__":
    PeopleCount(args)
