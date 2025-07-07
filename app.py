from flask import Flask,render_template,Response
import cv2
import mediapipe as mp
import numpy as np
import base64
import json

app = Flask(__name__)

cam = cv2.VideoCapture(0) 
mphands = mp.solutions.hands
hands = mphands.Hands(max_num_hands = 1)
mpDraw = mp.solutions.drawing_utils
canvas = np.zeros((471, 636, 3)) + 255

drawColor = (0,0,0)
brushthick = 6
prev_tip = None

def webcam():
    global prev_tip, canvas
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

        # Encode canvas as JPEG
        _, canvas_buffer = cv2.imencode(".jpg", canvas)
        canvas_b64 = base64.b64encode(canvas_buffer).decode("utf-8")

        # Encode video frame as JPEG
        _, frame_buffer = cv2.imencode(".jpg", img)
        frame_b64 = base64.b64encode(frame_buffer).decode("utf-8")

        # Yield frame and draw data
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame_buffer.tobytes() + b'\r\n'
            b'Content-Type: text/plain\r\n\r\n' + json.dumps({
                "canvas": canvas_b64
            }).encode("utf-8") + b'\r\n'
        )

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(webcam(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug = True)