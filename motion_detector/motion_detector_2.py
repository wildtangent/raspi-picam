# import packages
import argparse
import datetime
import imutils
import time
import cv2

# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

# Parse args
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to video")
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
ap.add_argument("-p", "--picamera", type=bool, default=True, help="use the picamera instead of usb webcam")
ap.add_argument("-t", "--threshold", type=int, default=25, help="set threshold for frame delta")
args = vars(ap.parse_args())

# Init first frame
firstFrame = None


# Parse video arg
if args.get("picamera", None) is True:
  # initialize the camera and grab a reference to the raw camera capture
  cameraType = "picamera"
  camera = PiCamera()
  camera.resolution = (640, 480)
  camera.framerate = 32
  rawCapture = PiRGBArray(camera, size=(640, 480))
  time.sleep(0.1)

elif args.get("video", None) is None:
  cameraType = "webcam"
  camera = cv2.VideoCapture(0)
  time.sleep(0.25)

# Otherwise get file
else:
  cameraType = "file"
  camera = cv2.VideoCapture(args["video"])


def processCameraFrame(frame):
  global firstFrame

  text = "Unoccupied"
  # resixe frame, convert to grayscale, blur
  frame = imutils.resize(frame, width=500)

  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  gray = cv2.GaussianBlur(gray, (21, 21), 0)

  # if first frame is none, make it gray
  if firstFrame is None:
    firstFrame = gray
    return False

  # compute absolute difference between first and current frame
  # first frame
  frameDelta = cv2.absdiff(firstFrame, gray)
  thresh = cv2.threshold(frameDelta, args.get("threshold", None), 255, cv2.THRESH_BINARY)[1]

  # idlate threshod image to fill holes
  # on thresholded image
  thresh = cv2.dilate(thresh, None, iterations=2)
  (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

  # loop over the contours
  for c in cnts:

    # if the contour is small, ignore and move on to next one
    if cv2.contourArea(c) < args["min_area"]:
      continue
    
    # compute teh bounding box for teh contour
    # update th text
    (x, y, w,  h) = cv2.boundingRect(c)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    text = "Occupied"

  # draw the text and timestamp to the frame
  cv2.putText(frame, "Room status: {}".format(text), (10, 20),
     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
  cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
    (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

  cv2.imshow("Security Feed", frame)
  cv2.imshow("Thresh", thresh)
  cv2.moveWindow("Thresh", 650, 0)
  cv2.imshow("Frame delta", frameDelta)
  cv2.moveWindow("Frame delta", 0, 500)

def checkKeyInput():
  key = cv2.waitKey(1)

  if key == ord("q"):
    return False

def cameraLoop():
  if cameraType == "picamera":
    global rawCapture
    global camera
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
      # grab the raw NumPy array representing the image, then initialize the timestamp
      # and occupied/unoccupied text
      frame = frame.array
      grabbed = True

      if processCameraFrame(frame) == False:
        rawCapture.truncate(0)
        continue

      if checkKeyInput() == False:
        break

      # clear the stream in preparation for the next frame
      rawCapture.truncate(0)

    cv2.destroyAllWindows()  

  else:
    # loop over frames of video
    while True:
      # Grab current frame and
      # init text
      (grabbed, frame) = camera.read()
      print(grabbed)
      # If frame not grabbed, quit
      # the ideo
      if not grabbed:
        break

      if processCameraFrame(frame) == False:
        continue

      if checkKeyInput() == False:
        break


    camera.release()
    cv2.destroyAllWindows()

# Run the main loop
cameraLoop()


