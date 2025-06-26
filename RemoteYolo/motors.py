import time
import requests

last_seen = None

while True:
    try:
        response = requests.get("http://10.42.0.114:5000/get_class_id")
        if response.status_code == 200:
            class_id = response.json().get("class_id")
            if class_id != last_seen and class_id is not None:
                print(f"[MOTOR] New class_id received: {class_id}")
                last_seen = class_id
        else:
            print("[MOTOR] Failed to get class_id")

    except Exception as e:
        print(f"[MOTOR] Error: {e}")

    time.sleep(1)
