from imutils.video import VideoStream
from imutils.video import FPS
import argparse
import imutils
import time
import cv2
import os
import shutil

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str, help="path to input video file")
ap.add_argument("-t", "--tracker", type=str, default="kcf", help="OpenCV object tracker type")
ap.add_argument("-d", "--dir_name", type=str, default=str(time.time()), help="OpenCV object tracker type")
args = vars(ap.parse_args())

(major, minor) = cv2.__version__.split(".")[:2]

if int(major) == 3 and int(minor) < 3:
    tracker = cv2.Tracker_create(args["tracker"].upper())

else:
    OPENCV_OBJECT_TRACKERS = {
        "csrt": cv2.TrackerCSRT_create,
		"kcf": cv2.TrackerKCF_create,
		# "boosting": cv2.TrackerBoosting_create,
		# "mil": cv2.TrackerMIL_create,
		# "tld": cv2.TrackerTLD_create,
		# "medianflow": cv2.TrackerMedianFlow_create,
		# "mosse": cv2.TrackerMOSSE_create
	}
    tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()
initBB = None

# if a video path was not supplied, grab the reference to the web cam
if not args.get("video", False):
    print("[INFO] starting video stream...")
    vs = VideoStream(src=0).start()
    time.sleep(1.0)
# otherwise, grab a reference to the video file
else:
    vs = cv2.VideoCapture(args["video"])
# initialize the FPS throughput estimator
fps = None
# loop over frames from the video stream
points=[]
frames=[]
max_w=0
max_h=0
sleep_time=0.1
while True:
	# grab the current frame, then handle if we are using a
	# VideoStream or VideoCapture object
    frame = vs.read()
    frame = frame[1] if args.get("video", False) else frame
    time.sleep(sleep_time)
	# check to see if we have reached the end of the stream
    if frame is None:
        break
	# resize the frame (so we can process it faster) and grab the
	# frame dimensions
    (H, W) = frame.shape[:2]
    # check to see if we are currently tracking an object
    if initBB is not None:
        sleep_time=0
		# grab the new bounding box coordinates of the object
        (success, box) = tracker.update(frame)
		# check to see if the tracking was a success
        if success:
            (x, y, w, h) = [int(v) for v in box]
            if(max_w<w):
                max_w=w
            if(max_h<h):
                max_h=h
            points.append((x+int(w/2),y+int(h/2)))
            frames.append(frame)
            #cv2.rectangle(frame, (x, y), (x + w, y + h),(0, 255, 0), 2)
		# update the FPS counter
        fps.update()
        fps.stop()
		# initialize the set of information we'll be displaying on
		# the frame
        info = [
			("Tracker", args["tracker"]),
			("Success", "Yes" if success else "No"),
			("FPS", "{:.2f}".format(fps.fps())),
		]
		# loop over the info tuples and draw them on our frame
        for (i, (k, v)) in enumerate(info):
            text = "{}: {}".format(k, v)
            #cv2.putText(frame, text, (10, H - ((i * 20) + 20)),cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    # show the output frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    # if the 's' key is selected, we are going to "select" a bounding
    # box to track
    if key == ord("s"):
        # select the bounding box of the object we want to track (make
        # sure you press ENTER or SPACE after selecting the ROI)
        initBB = cv2.selectROI("Frame", frame, fromCenter=False,showCrosshair=True)
        # start OpenCV object tracker using the supplied bounding box
        # coordinates, then start the FPS throughput estimator as well
        tracker.init(frame, initBB)
        fps = FPS().start()    
        # if the `q` key was pressed, break from the loop
    elif key == ord("q"):
        break
# if we are using a webcam, release the pointer
if not args.get("video", False):
    vs.stop()
# otherwise, release the file pointer
else:
    vs.release()
# close all windows
cv2.destroyAllWindows()

if args.get("dir_name", False):
    dir_name=f'crops\{args["dir_name"]}_{str(time.time())}'
else:
    dir_name=f'crops\img_from_vid_{str(args["dir_name"])}'

if os.path.exists(dir_name):
    shutil.rmtree(dir_name)

os.mkdir(dir_name)

counter=10
for frame,point in zip(frames,points):
    w1=point[0]-int(max_w/2)
    w2=w1+max_w
    h1=point[1]-int(max_h/2)
    h2=h1+max_h
    print(w1,w2,h1,h2)
    cv2.imwrite(f'{dir_name}\{str(counter)}.png',frame[h1:h2,w1:w2])
    counter+=1


video_name = os.path.join(dir_name, "video.mp4")

images = [img for img in os.listdir(dir_name) if img.endswith(".png")]

video = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), 30, (max_w,max_h))

for image in images:
    video.write(cv2.imread(os.path.join(dir_name, image)))

cv2.destroyAllWindows()
video.release()