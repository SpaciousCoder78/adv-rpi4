from flask import Flask, request, Response, jsonify
import cv2
import requests

app = Flask(__name__)

camera = cv2.VideoCapture(0)

label = None

def generate_frames():
    while True:
        success, frame = camera.read()

        if not success:
            break
        else:
            # Get current class_ids from analysis server
            current_class_ids = get_class_ids_from_analyse()
            if current_class_ids:
                print(f"Current detections: {current_class_ids}")
                label = current_class_ids[0]
                print(type(label))
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
@app.route('/video_feed')

def video_feed() :
    return Response(generate_frames(), mimetype = 'multipart/x-mixed-replace; boundary=frame')
    


@app.route('/receive_data', methods=['GET'])
def receive_data():
    global label
    # For GET requests, data comes from URL parameters
    data = request.args.get('class_ids')  # Get class_ids from URL parameters
    if data:
        try:
            # Convert string back to list if it's JSON format
            import json
            class_ids = json.loads(data)
            # Convert all class IDs to integers
            label = [int(class_id) for class_id in class_ids] if isinstance(class_ids, list) else int(class_ids)
            print(f"Received class IDs (as int): {label}")
            return jsonify({"message": "Data received", "received": label}), 200
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON data"}), 400
    else:
        return jsonify({"error": "No data received"}), 400

def get_class_ids_from_analyse():
    """
    Fetch current class_ids from rpi_analyse.py server
    
    Returns:
        list: Current class IDs from the analysis server
    """
    try:
        response = requests.get("http://10.42.0.114:5000/get_label", timeout=2)
        if response.status_code == 200:
            data = response.json()
            return data.get("current_label", [])
        else:
            print(f"Error fetching class_ids: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Connection error to analysis server: {e}")
        return []

@app.route('/get_label', methods=['GET'])
def get_label():
    global label
    return jsonify({"current_label": label}), 200

@app.route('/get_live_class_ids', methods=['GET'])
def get_live_class_ids():
    """
    Get the current class_ids from the analysis server
    """
    class_ids = get_class_ids_from_analyse()
    return jsonify({"live_class_ids": class_ids}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
    print(label)


