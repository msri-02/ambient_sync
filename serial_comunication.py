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
dummy = "6, 255, 1, 1, 2, 2, 255, 255, 1, 1, 2, 2, 255, 255, 1, 1, 3, 255, 3, 9999"
dummy2 = "60, 5, 138, 255, 85, 53, 255, 238, 45, 255, 255, 33, 255, 255, 8, 255, 255, 4, 255, 255, 3, 255, 255, 15, 60, 255, 17, 62, 255, 180, 50, 255, 180, 50, 255, 168, 41, 255, 255, 48, 255, 255, 48, 255, 255, 48, 255, 255, 48, 255, 255, 48, 255, 255, 73, 255, 255, 86, 5, 138, 255, 5, 138, 255, 5, 138, 255, 5, 138, 255, 5, 138, 255, 5, 138, 255, 3, 141, 255, 3, 216, 255, 3, 216, 255, 3, 255, 255, 5, 255, 255, 68, 255, 160, 242, 255, 131, 255, 255, 123, 255, 255, 158, 255, 255, 84, 255, 255, 80, 255, 255, 0, 255, 255, 6, 255, 255, 13, 255, 255, 61, 255, 255, 48, 255, 255, 44, 255, 180, 50, 255, 180, 50, 255, 180, 50, 255, 180, 45, 255, 15, 60, 255, 15, 60, 255, 3, 255, 255, 3, 255, 255, 11, 255, 255, 8, 255, 255, 33, 255, 255, 33, 255, 85, 53, 255, 85, 53, 255, 5, 138, 255, 5, 138, 255, 3, 216, 255, 3, 216, 255, 2, 216, 255, 5, 255, 255, 85, 241, 255, 9999"
dummy3 = "10, 5, 138, 255, 255, 3, 255, 255, 255, 48, 255, 255, 86, 5, 138, 255, 3, 141, 255, 242, 255, 131, 255, 255, 6, 255, 180, 50, 255, 180, 50, 255, 11, 255, 5, 138, 255, 85, 241, 255, 9999"
data = dummy

control_arduino_led("COM3", 115200, data)