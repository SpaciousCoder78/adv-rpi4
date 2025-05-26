import cv2
import time
import threading
from flask import Flask, Response

app = Flask(__name__)

camera = cv2.VideoCapture(0)

camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
camera.set(cv2.CAP_PROP_FPS,30)

frame = None
lock = threading.Lock()

def capture_frame():
	global frame
	while True:
		ret, f = camera.read()
		if ret:
			with lock:
				frame = f

def generate():
	global frame
	while True:
		if frame is not None:
			with lock:
				ret, jpeg = cv2.imencode('.jpg', frame)
				if ret:
					frame_data = jpeg.tobytes()
					yield(b'--frame\r\n'
					      b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n\r\n')

@app.route('/video_feed')

def video_feed():
	return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
	threading.Thread(target=capture_frame, daemon=True).start()
	app.run(host='0.0.0.0', port=5000, debug = False)	
