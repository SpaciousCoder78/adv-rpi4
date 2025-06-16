import cv2
import threading
import RPi.GPIO as GPIO
from time import sleep
from yolov8 import YOLOv8

# Global variables to share state
detected_class = None
detection_triggered = False

def controlspeed():
    global detected_class, detection_triggered

    # Motor A pins (Motor 1)
    in1 = 24
    in2 = 23
    ena = 25

    # Motor B pins (Motor 2)
    in3 = 17
    in4 = 22
    enb = 27

    temp1 = 1  # 1 for forward

    GPIO.setmode(GPIO.BCM)

    # Setup Motor A
    GPIO.setup(in1, GPIO.OUT)
    GPIO.setup(in2, GPIO.OUT)
    GPIO.setup(ena, GPIO.OUT)
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.LOW)
    pA = GPIO.PWM(ena, 1000)
    pA.start(20)

    # Setup Motor B
    GPIO.setup(in3, GPIO.OUT)
    GPIO.setup(in4, GPIO.OUT)
    GPIO.setup(enb, GPIO.OUT)
    GPIO.output(in3, GPIO.LOW)
    GPIO.output(in4, GPIO.LOW)
    pB = GPIO.PWM(enb, 1000)
    pB.start(20)

    count = 1
    while True:
        print("Motor thread running")
        if temp1 == 1:
            # Forward for both motors
            GPIO.output(in1, GPIO.HIGH)
            GPIO.output(in2, GPIO.LOW)
            GPIO.output(in3, GPIO.HIGH)
            GPIO.output(in4, GPIO.LOW)
            print("forward")
            pA.ChangeDutyCycle(50)
            pB.ChangeDutyCycle(50)
            sleep

            # Check if detected class is 29 to perform stopping actions
            if detected_class == 29:
                print("Detected 70 Speed Sign")
                detection_triggered = True

                pA.ChangeDutyCycle(70)
                pB.ChangeDutyCycle(70)
                
                
            if detected_class == 30:
                print("Detected 20 Speed Sign")
                detection_triggered=True
                
                pA.ChangeDutyCycle(20)
                pB.ChangeDutyCycle(20)
                

outer_run = True
while outer_run:
    # Initialize the camera and YOLOv8 detector for each run.
    cap = cv2.VideoCapture(0)
    model_path = "model.onnx"
    yolov8_detector = YOLOv8(model_path, conf_thres=0.5, iou_thres=0.5)
    
    cv2.namedWindow("Detected Objects", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Detected Objects", 800, 600)  # resize window to 800x600

    # Reset globals
    detected_class = None
    detection_triggered = False

    # Start the motor thread as a daemon.
    motor_thread = threading.Thread(target=controlspeed, daemon=True)
    motor_thread.start()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        boxes, scores, class_ids = yolov8_detector(frame)
        combined_img = yolov8_detector.draw_detections(frame)

        if class_ids:
            detected_class = class_ids[0]
        else:
            detected_class = None

        cv2.imshow("Detected Objects", combined_img)
        print("Detected class:", detected_class)

        # If detection_triggered is True and detected_class goes to None, restart.
        if detection_triggered and detected_class is None:
            print("Detected class is None after detection 29; restarting loop.")
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            outer_run = False
            break

    cap.release()
    cv2.destroyAllWindows()
