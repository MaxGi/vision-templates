#!/usr/bin/env python3

#Modified version of depthai example gen2-people-tracker

from depthai_sdk import OakCamera, TrackerPacket, Visualizer, TextPosition
import depthai as dai
from people_tracker import PeopleTracker, Zone
import cv2

replayPath = ""
pt = PeopleTracker()
zones = []

def draw_circle(event,x,y,flags,param):
    global mouseX,mouseY
    if event == cv2.EVENT_LBUTTONDBLCLK:
        print(x, y)

with OakCamera(replay=replayPath) as oak:
    color_cam = oak.create_camera('color')
    tracker = oak.create_nn('person-detection-retail-0013', color_cam, tracker=True)
    tracker.config_nn(conf_threshold=0.3)
    tracker.config_tracker(tracker_type=dai.TrackerType.ZERO_TERM_COLOR_HISTOGRAM, track_labels=[1])

    f = open("zones.txt", "r")
    for line in f:
        split = line.split(" ") 
        x1 = int(split[0])
        y1 = int(split[1])
        x2 = int(split[2])
        y2 = int(split[3])
        zones.append(Zone((x1, y1), (x2, y2)))
        print("Line: ", line)

    print("NUM ZONES: ", len(zones))

    cv2.namedWindow('People Tracker')
    cv2.setMouseCallback('People Tracker',draw_circle)

    def cb(packet: TrackerPacket, vis: Visualizer):
        
        left, right, up, down = pt.calculate_tracklet_movement(packet.daiTracklets)
        vis.add_text("Listen to port 5005 for message people-tracker", position=TextPosition.TOP_LEFT, size=1)

        vis.draw(packet.frame)
        
        for id in pt.data:
            for z in zones:
                z.people_pos(pt.data[id]['coords'])
        

        for z in zones:
            z.draw(packet.frame)
        cv2.imshow('People Tracker', packet.frame)


    
    oak.visualize(tracker.out.tracker, callback=cb)
    oak.start(blocking=True)
