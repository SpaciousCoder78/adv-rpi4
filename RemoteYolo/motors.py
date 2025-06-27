import time
import requests
import RPi.GPIO as GPIO
from threading import Lock

# === Labels Map ===
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

# === Motor Logic ===
DEFAULT_SPEED = 20
current_speed = DEFAULT_SPEED  # Ensure it starts at default
current_action = 'Forward'
lock = Lock()

def set_motors(speed):
    GPIO.output(in1, GPIO.HIGH)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.HIGH)
    GPIO.output(in4, GPIO.LOW)
    pA.ChangeDutyCycle(speed)
    pB.ChangeDutyCycle(speed)
    print(f"[MOTOR] Moving forward at {speed}%")

def stop_motors():
    pA.ChangeDutyCycle(0)
    pB.ChangeDutyCycle(0)
    print("[MOTOR] Motors stopped")

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
                print(f"[MOTOR] Couldn't parse speed from label: {predicted_label}")
        elif predicted_label in ['Stop', 'Red Light']:
            current_speed = 0
            current_action = 'Stop'
            stop_motors()
        elif predicted_label == 'Green Light':
            if current_action == 'Stop':
                current_speed = DEFAULT_SPEED  # Reset to default on green light
                current_action = 'Forward'
                set_motors(current_speed)
        elif predicted_label is None:
                set_motors(20)

# === Start at default speed ===
set_motors(DEFAULT_SPEED)

# === Polling Loop ===
last_seen = None

try:
    while True:
        try:
            response = requests.get("http://10.42.0.114:5000/get_class_id")
            if response.status_code == 200:
                class_id = response.json().get("class_id")
                if class_id is not None and class_id != last_seen:
                    last_seen = class_id
                    try:
                        class_id = int(class_id)
                        if 0 <= class_id < len(LABELS):
                            label = LABELS[class_id]
                            print(f"[MOTOR] Received class_id: {class_id}, Label: {label}")
                            update_action(label)
                        else:
                            print(f"[MOTOR] Unknown class_id: {class_id}")
                    except ValueError:
                        print(f"[MOTOR] Non-integer class_id received: {class_id}")
                elif class_id is None:
                    print("class id is none")
                    update_action(None)
            else:
                print("[MOTOR] Failed to get class_id")
        except Exception as e:
            print(f"[MOTOR] Error: {e}")

        time.sleep(1)

except KeyboardInterrupt:
    print("[MOTOR] Interrupted. Cleaning up...")
    current_speed = DEFAULT_SPEED
    print(f"[MOTOR] Speed reset to default: {DEFAULT_SPEED}")
    GPIO.cleanup()
