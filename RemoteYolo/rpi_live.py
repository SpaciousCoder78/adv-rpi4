from flask import Flask, Response, request, jsonify
import cv2

app = Flask(__name__)
camera = cv2.VideoCapture(0)

latest_class_id = None  # Shared variable

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/receive_detection', methods=['POST'])
def receive_detection():
    global latest_class_id
    data = request.get_json()
    latest_class_id = data.get("class_id")
    print(f"Received class_id: {latest_class_id}")
    return {"status": "received"}, 200

@app.route('/get_class_id', methods=['GET'])
def get_class_id():
    return jsonify({"class_id": latest_class_id}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)