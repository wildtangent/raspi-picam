# import packages
import argparse
import datetime
import imutils
import time
import cv2

# Parse args
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to video")
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
args = vars(ap.parse_args())

# PArse video arg
if args.get("video", None) is None:
  camera = cv2.VideoCapture(0)
  time.sleep(0.25)

# Otherwise get file
else:
  camera = cv2.VideoCapture(args["video"])

# Init first frame
firstFrame = None

# loop over frames of video
while True:
  # Grab current frame and
  # init text
  (grabbed, frame) = camera.read()
  text = "Unoccupied"
  print(grabbed)
  # If frame not grabbed, quit
  # the ideo
  if not grabbed:
    break

  # resixe frame, convert to grayscale, blur
  frame = imutils.resize(frame, width=500)
  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  gray = cv2.GaussianBlur(gray, (21, 21), 0)

  # if first frame is none, make it gray
  if firstFrame is None:
    firstFrame = gray
    continue

  # compute absolute difference between first and current frame
  # first frame
  framedelta = cv2.absdiff(firstFrame, gray)
  thresh = cv2.threshhold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

  # idlate threshod image to fill holes
  # on thresholded image
  thresh = cv2.dilate(thresh, None, iterations=2)
  (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

  
  # loop over the contours
  for c in cnts:
    # if the contour is small, igrore
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
  cv2.imshow("Frame delta", frameDelta)
  key = cv2.waitKey(1)

  if key == ord("q"):
    break

camera.release()
cv2.destroyAllWindows()


