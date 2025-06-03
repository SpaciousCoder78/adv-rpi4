from flask import Flask, Response
import cv2
from picamera2 import Picamera2

app = Flask(__name__)

picam = Picamera2()
preview_config = picam.create_preview_configuration(main={"size": (640, 480)})  # adjust resolution as needed
picam.configure(preview_config)
picam.start()

def generate_frames():
    while True:
        frame = picam.capture_array()
        # Convert BGR (default) to RGB to fix inverted colors.
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
