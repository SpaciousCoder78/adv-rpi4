import RPi.GPIO as GPIO
from time import sleep

# Motor A pins (Motor 1)
in1 = 24
in2 = 23
ena = 25

# Motor B pins (Motor 2) - update these as per your hardware connections
in3 = 17
in4 = 22
enb = 26

temp1 = 1  # 1 for forward, 0 for backward

GPIO.setmode(GPIO.BCM)

# Setup Motor A
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(ena, GPIO.OUT)
GPIO.output(in1, GPIO.LOW)
GPIO.output(in2, GPIO.LOW)
pA = GPIO.PWM(ena, 1000)
pA.start(25)

# Setup Motor B
GPIO.setup(in3, GPIO.OUT)
GPIO.setup(in4, GPIO.OUT)
GPIO.setup(enb, GPIO.OUT)
GPIO.output(in3, GPIO.LOW)
GPIO.output(in4, GPIO.LOW)
pB = GPIO.PWM(enb, 1000)
pB.start(25)

print("\n")
print("Default speed & direction of motors is LOW & Forward.....")
print("Commands: r-run s-stop f-forward b-backward l-low m-medium h-high e-exit")
print("\n")    

while True:
    x = input()
    
    if x == 'r':
        print("run")
        if temp1 == 1:
            # Forward for both motors
            GPIO.output(in1, GPIO.HIGH)
            GPIO.output(in2, GPIO.LOW)
            GPIO.output(in3, GPIO.HIGH)
            GPIO.output(in4, GPIO.LOW)
            print("forward")
        else:
            # Backward for both motors
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.HIGH)
            GPIO.output(in3, GPIO.LOW)
            GPIO.output(in4, GPIO.HIGH)
            print("backward")

    elif x == 's':
        print("stop")
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.LOW)
        GPIO.output(in3, GPIO.LOW)
        GPIO.output(in4, GPIO.LOW)

    elif x == 'f':
        print("forward")
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
        GPIO.output(in3, GPIO.HIGH)
        GPIO.output(in4, GPIO.LOW)
        temp1 = 1

    elif x == 'b':
        print("backward")
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.HIGH)
        GPIO.output(in3, GPIO.LOW)
        GPIO.output(in4, GPIO.HIGH)
        temp1 = 0

    elif x == 'l':
        print("low")
        pA.ChangeDutyCycle(25)
        pB.ChangeDutyCycle(25)

    elif x == 'm':
        print("medium")
        pA.ChangeDutyCycle(50)
        pB.ChangeDutyCycle(50)

    elif x == 'h':
        print("high")
        pA.ChangeDutyCycle(75)
        pB.ChangeDutyCycle(75)
        
    elif x == 'e':
        GPIO.cleanup()
        print("GPIO Clean up")
        break
    
    else:
        print("<<< wrong data >>>")
        print("please enter one of: r, s, f, b, l, m, h, e")