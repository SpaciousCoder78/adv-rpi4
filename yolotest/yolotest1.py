import cv2
import threading
import RPi.GPIO as GPIO
from time import sleep
from yolov8.YOLOv8 import YOLOv8  # Make sure this is in a proper Python module

LABELS = [
    'Green Light', 'Red Light', 'Speed Limit 10', 'Speed Limit 100',
    'Speed Limit 110', 'Speed Limit 120', 'Speed Limit 20', 'Speed Limit 30',
    'Speed Limit 40', 'Speed Limit 50', 'Speed Limit 60', 'Speed Limit 70',
    'Speed Limit 80', 'Speed Limit 90', 'Stop'
]

# === GPIO Setup ===
in1, in2, ena = 24, 23, 25
in3, in4, enb = 17, 22, 27

GPIO.setmode(GPIO.BCM)
GPIO.setup([in1, in2, ena, in3, in4, enb], GPIO.OUT)

pA = GPIO.PWM(ena, 1000)
pB = GPIO.PWM(enb, 1000)
pA.start(0)
pB.start(0)

# === Global Variables ===
current_speed = 20  # Default speed
current_action = 'Forward'
lock = threading.Lock()

# === Motor Control ===
def set_motors(speed):
    GPIO.output(in1, GPIO.HIGH)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.HIGH)
    GPIO.output(in4, GPIO.LOW)
    pA.ChangeDutyCycle(speed)
    pB.ChangeDutyCycle(speed)
    print(f"Moving forward at {speed}%")

def stop_motors():
    pA.ChangeDutyCycle(0)
    pB.ChangeDutyCycle(0)
    print("Motors stopped")

def update_action(predicted_label):
    global current_speed, current_action
    with lock:
        if 'Speed Limit' in predicted_label:
            try:
                speed_val = int(predicted_label.split()[-1])
                pwm = max(10, min((speed_val / 120) * 100, 100))
                current_speed = int(pwm)
                current_action = 'Forward'
                set_motors(current_speed)
            except ValueError:
                print(f"Couldn't parse speed from label: {predicted_label}")
        elif predicted_label in ['Stop', 'Red Light']:
            current_speed = 0
            current_action = 'Stop'
            stop_motors()
        elif predicted_label == 'Green Light':
            if current_action == 'Stop':
                current_action = 'Forward'
                set_motors(current_speed)

# === Detection Loop ===
def detection_loop():
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Detected Objects", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Detected Objects", 800, 600)

    model_path = "best.onnx"  # Use optimized/quantized model
    yolov8_detector = YOLOv8(model_path, conf_thres=0.5, iou_thres=0.5)

    cv2.namedWindow("Detected Objects", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Detected Objects", 640, 480)
    #cv2.resizeWindow("Detected Objects", 320, 240)

    last_label = None
    set_motors(current_speed)  # Start at 20

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break


        boxes, scores, class_ids = yolov8_detector(frame)
        combined_img = yolov8_detector.draw_detections(frame)

        if class_ids is not None and len(class_ids) > 0:
            class_id = int(class_ids[0])
            if class_id < len(LABELS):
                label = LABELS[class_id]
                print(f"Detected: {label}")
                if label != last_label:
                    update_action(label)
                    last_label = label

        cv2.imshow("Detected Objects", combined_img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()

if __name__ == "__main__":
    try:
        detection_loop()
    except KeyboardInterrupt:
        print("Interrupted. Cleaning up...")
        GPIO.cleanup()
