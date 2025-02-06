import os
from common.vehicle_type import VehicleType
import cv2

def processVideo(id:int, vid:os.path, type:VehicleType):
    video = cv2.VideoCapture(vid)
    video.write_videofile(f"processed_videos/processed_{id}.mp4")

    path = f"processed_videos/processed_{id}.mp4"
    capture = cv2.VideoCapture(path)

    # define object detection model
    bike_cascade = cv2.CascadeClassifier("models/bike.xml")

    # initialise frame
    frame_data = []
    frame_number = 1

    # TODO : change from while True to something more fail-safe
    while True:
        ret, frame = capture.read()

        if (ret):
            # detect bikes
            grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            bikes = bike_cascade.detectMultiScale(grey, 1.1, 0)

            for (x, y, w, h) in bikes:
                # cv2.rectangle(frame, (x,y), (x+w,y+h), (0,0,255), 2)
                frame_data.append((frame_number, int(x),int(y),int(w),int(h)))

            frame_number += 1
            # cv2.imshow('frame', frame)

        else:
            break
    
    capture.release()


    os.remove(f"processed_videos/processed_{id}.mp4")
    os.remove(vid)
    pass