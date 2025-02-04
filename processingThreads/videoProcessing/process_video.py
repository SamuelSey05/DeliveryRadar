import os
from common.vehicle_type import VehicleType
import cv2
from ultralytics import YOLO
import time
import datetime
import numpy as np

def processVideo(id:int, vid:os.path, type:VehicleType):

    # TODO : move this somewhere else, don't what it to run every time the function is called
    model = YOLO('yolov8n.pt')

    # class ID of 'bicycle' in the model
    BIKE_ID = 1

    video = cv2.VideoCapture(vid)
    video.write_videofile(f"processed_videos/processed_{id}.mp4")

    path = f"processed_videos/processed_{id}.mp4"
    
    # set stream to True to analyse by frame
    # can add show=True to see detection
    # TODO : look into not using stream, instead processing whole video at once
    results = model(source=path, stream=True)

    # after loop will contains a list of (frame_number, x, y, w, h)
    bike_data = []

    for frame_number, result in enumerate(results):
        # TODO : account for multiple bikes, currently using a dictionary to only get one bike
        detected_objects = {int(class_id):pos for class_id,pos in zip(result.boxes.cls.tolist(), result.boxes.xywh.tolist())}

        if (BIKE_ID in detected_objects.keys()):
            x, y, w, h = detected_objects[BIKE_ID]
            bike_data.append((frame_number, x, y, w, h))


    os.remove(path)
    os.remove(vid)
    pass