import numpy as np
import cv2


  
cap = cv2.VideoCapture(1)
  
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))


zones = [[(500,250), (550,300)],
         [(350,100), (400,140)],
         [(300,300), (350,350)],
         [(200,200), (250,250)]]
  
# initializing subtractor 
fgbg = cv2.bgsegm.createBackgroundSubtractorGMG()
  
while(1):
    ret, frame = cap.read()
    
    # applying on each frame
    fgmask = fgbg.apply(frame)
  
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)     
    
    for z in zones:
        cv2.rectangle(frame, z[0], z[1], (255, 0, 0), 1)


    cv2.imshow('frame', fgmask)
    cv2.imshow('clr', frame)

    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
  
cap.release()
cv2.destroyAllWindows()