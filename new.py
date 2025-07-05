import cv2 
import cvzone
import numpy as np
import mediapipe as mp 

cam = cv2.VideoCapture(0) 
mphands = mp.solutions.hands
hands = mphands.Hands(max_num_hands = 1)
mpDraw = mp.solutions.drawing_utils
canvas = np.zeros((471, 636, 3)) + 255

drawColor = (0,0,0)
brushthick = 6
prev_tip = None


while True:
    sucess,img = cam.read()
    img = cv2.flip(img,1)
    imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    result = hands.process(imgRGB)
    if result.multi_hand_landmarks:
        for handlms in result.multi_hand_landmarks:
            mpDraw.draw_landmarks(img,handlms,mphands.HAND_CONNECTIONS,mpDraw.DrawingSpec(color=(146, 199, 199), thickness=1, circle_radius=1),mpDraw.DrawingSpec(color=(10,255,255), thickness=1, circle_radius=1))

            #cheak weather index finger is up
            h,w,_ = img.shape
            lm = handlms.landmark

            index_tip = int(lm[8].y * h)
            index_bot = int(lm[6].y * h)

            ring_tip = int(lm[12].y * h)
            ring_bol = int(lm[10].y * h)

            tip_center = (int(lm[8].x * w),int(lm[8].y * h))
            #print(index_tip,index_bot)

            if index_tip < index_bot and ring_tip > ring_bol:
                cv2.circle(img,center=tip_center,radius=7,color=(255,255,255),thickness=2 )
                if prev_tip is not None:
                    cv2.line(img,prev_tip,tip_center,drawColor,brushthick)
                    cv2.line(canvas,prev_tip,tip_center,drawColor,brushthick)
                prev_tip = tip_center

            else:
                prev_tip = None

            pinky_tip = int(lm[20].y * h)
            pinky_bol = int(lm[17].y * h)

        if index_tip > index_bot and ring_tip > ring_bol and pinky_tip < pinky_bol:
            canvas[:] = (255, 255, 255)  # change all canves into white




    cv2.imshow("Image",img)
    cv2.imshow("Canvas", canvas)
    if cv2.waitKey(1) & 0xFF == 27:
        break
cam.release()
cv2.destroyAllWindows()

