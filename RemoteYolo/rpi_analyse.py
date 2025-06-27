import cv2
import threading
import queue
from yolov8 import YOLOv8

def frame_reader(cap, frame_queue):
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        # Keep queue size small to avoid latency
        if not frame_queue.full():
            frame_queue.put(frame)

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

import requests

# Your existing YOLO inference loop...
while cap.isOpened():
    if not frame_queue.empty():
        while not frame_queue.empty():
            frame = frame_queue.get()

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes, scores, class_ids = yolov8_detector(frame_rgb)
        combined_rgb = yolov8_detector.draw_detections(frame_rgb)
        combined_img = cv2.cvtColor(combined_rgb, cv2.COLOR_RGB2BGR)

        # Send detected class_ids to rpi_live
        if len(class_ids) > 0:
            for class_id in class_ids:
                try:
                    response = requests.post(
                        "http://10.42.0.114:5000/receive_detection",
                        json={"class_id": int(class_id)}
                    )
                except requests.exceptions.RequestException as e:
                    print(f"Error sending detection: {e}")
        else:
            try:
                response = requests.post(
                    "http://10.42.0.114:5000/receive_detection",
                    json={"class_id": None}
                )
            except requests.exceptions.RequestException as e:
                print(f"Error sending detection: {e}")
        cv2.imshow("Detected Objects", combined_img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()