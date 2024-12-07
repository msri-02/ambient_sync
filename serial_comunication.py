import serial
import time

def control_arduino_led(port, baudrate, command):
    """
    Sends a command to the Arduino to control the onboard LED.

    Args:
        port (str): The serial port (e.g., 'COM3' or '/dev/ttyUSB0').
        baudrate (int): The baud rate (e.g., 9600).
        command (str): The command to send (e.g., '1,255,0,0,-1').
    """
    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            time.sleep(2)  # Wait for Arduino to reset after serial connection
            print(f"Connected to {port}. Sending command: {command}")
            ser.write((command + '\n').encode('utf-8'))  # Send the command
    except serial.SerialException as e:
        print(f"Serial error: {e}")

# data = "3, 255, 0, 0, 0, 255, 0, 0, 0, 255, 9999"
blue = "1, 0, 0, 255, 9999"
red = "1, 255, 0, 0, 9999" # allgreen 
green = "1, 0, 255, 0, 9999"
dummy = ""
data = dummy

control_arduino_led("COM3", 9600, data)