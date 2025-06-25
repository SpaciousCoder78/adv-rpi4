from flask import Flask, request, Response, jsonify
import cv2

app = Flask(__name__)
import threading
import queue
from yolov8 import YOLOv8
import requests


class_ids = []  # Initialize as empty list

def send_data_to_flask_server(data, url="http://10.42.0.114:5000/receive_data"):
    """
    Send data to the Flask server endpoint using GET request with URL parameters

    Args:
        data (list): The class IDs list to send to the server
        url (str): The URL of the Flask endpoint

    Returns:
        dict: The response from the server
    """
    try:
        import json
        # Convert data to JSON string for URL parameter
        data_json = json.dumps(data)

        # Send GET request with data as URL parameter
        response = requests.get(url, params={'class_ids': data_json})

        # Check if request was successful
        if response.status_code == 200:
            print("Data sent successfully!")
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the Flask app is running.")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def frame_reader(cap, frame_queue):
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        # Keep queue size small to avoid latency
        if not frame_queue.full():
            frame_queue.put(frame)



@app.route('/get_label', methods=['GET'])
def get_label():
    global class_ids
    return jsonify({"current_label": class_ids}), 200

if __name__ == '__main__':
    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5001, debug=False))
    flask_thread.daemon = True
    flask_thread.start()
    
    # Initialize video feed
    video_url = "http://10.42.0.114:5000/video_feed"
    cap = cv2.VideoCapture(video_url)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 60)

    # Initialize YOLOv8 detector
    model_path = "models/best.onnx"
    yolov8_detector = YOLOv8(model_path, conf_thres=0.5, iou_thres=0.5)

# Queue and reader thread for frame capture
    frame_queue = queue.Queue(maxsize=5)
    reader_thread = threading.Thread(target=frame_reader, args=(cap, frame_queue))
    reader_thread.daemon = True
    reader_thread.start()

    cv2.namedWindow("Detected Objects", cv2.WINDOW_NORMAL)

    while cap.isOpened():
        if not frame_queue.empty():
            # Retrieve only the most recent frame to reduce delay
            while not frame_queue.empty():
                frame = frame_queue.get()

            # Run detection and drawing
            # Convert frame from BGR to RGB for accurate detection
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes, scores, detected_class_ids = yolov8_detector(frame_rgb)
            combined_rgb = yolov8_detector.draw_detections(frame_rgb)
            combined_img = cv2.cvtColor(combined_rgb, cv2.COLOR_RGB2BGR)
            cv2.imshow("Detected Objects", combined_img)
            print(detected_class_ids)
            
            # Convert numpy array to list for JSON serialization
            class_ids_list = detected_class_ids.tolist() if hasattr(detected_class_ids, 'tolist') else list(detected_class_ids)
            
            # Update global class_ids and send to server
            class_ids = class_ids_list
            result = send_data_to_flask_server(class_ids_list)
            if result:
                print("Data sent to server:", result)


        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

