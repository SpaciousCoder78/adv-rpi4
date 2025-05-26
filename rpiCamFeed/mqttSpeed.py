import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

MQTT_BROKER = '192.168.137.236'
MQTT_TOPIC= 'car/speed'

motor_a = 24
motor_b = 23
enable_motor = 25

GPIO.setmode(GPIO.BCM)
#motor setup
GPIO.setup(motor_a,GPIO.OUT)
GPIO.setup(motor_b,GPIO.OUT)
GPIO.setup(enable_motor, GPIO.OUT)

#pmw_setup
dc_pwm=GPIO.PWM(enable_motor,1000)
dc_pwm.start(0)

GPIO.output(motor_a,GPIO.HIGH)
GPIO.output(motor_b,GPIO.LOW)
def on_message(client, userdata, msg):
	speed = int(msg.payload.decode())
	print(f"Received Spedd : {speed}")
	dc_pwm.ChangeDutyCycle(speed)

client = mqtt.Client()
client.connect(MQTT_BROKER, 1883, 60)
client.subscribe(MQTT_TOPIC)

client.on_message = on_message
client.loop_forever()
