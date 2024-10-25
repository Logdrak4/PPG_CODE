import RPi.GPIO as GPIO
import time
import os
import subprocess

# GPIO Setup
BUTTON_PIN = 17  # Use the GPIO pin number for your button
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Pull-up resistor

# Modes
mode = "Register a new user"  # Start in register mode

try:
    print(f"Current mode: {mode}")
    while True:
        button_state = GPIO.input(BUTTON_PIN)
        
        # Detect button press (when the button is pressed, the state goes LOW)
        if button_state == GPIO.LOW:
            time.sleep(0.2)  # Debounce delay
            if GPIO.input(BUTTON_PIN) == GPIO.LOW:  # Check if the button is still pressed
                # Toggle mode
                if mode == "Register a new user":
                    mode = "Authenticate a user"
                else:
                    mode = "Register a new user"
                
                print(f"Current mode: {mode}")
                time.sleep(0.5)  # Prevent multiple toggles

                # Run corresponding scripts based on mode
                if mode == "Register a new user":
                    video_file = input("Enter the video file path: ")
                    print("Running PPG and ID algorithm scripts...")
                    # Call the bash script with video file as an argument
                    subprocess.run(["bash", "your_bash_script.sh", video_file])
                elif mode == "Authenticate a user":
                    print("Authentication mode selected. Implement your logic here.")
                    # You can add logic for authentication mode if needed
                
        time.sleep(0.1)  # Polling delay to avoid high CPU usage

except KeyboardInterrupt:
    print("Exiting program.")
finally:
    GPIO.cleanup()  # Clean up GPIO settings
