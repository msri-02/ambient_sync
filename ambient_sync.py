import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
import os
import time
import glob
import scipy
import argparse
from scipy.ndimage import convolve
import serial
import time

def sendCommand(ser, command):
    ser.write((command + '\n').encode('utf-8'))  # Send serial command data

##################################################################################################

def euclidean_distance(point1, point2):
    distance = np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point1[1]) ** 2)  
    return distance  

##################################################################################################

def draw_line(image, point1, point2, color=(0, 255, 0), thickness=2):
    cv.line(image, point1, point2, color, thickness)
    return image

##################################################################################################

def perspective_warp(top_left, bottom_left, bottom_right, top_right, image):    
    source_points = np.array([top_left, bottom_left, bottom_right, top_right], dtype=np.float32)
    
    # set warp frame size
    width = 640
    height = 480

    destination_points = np.array([
    [0, 0],                     # Top-left corner
    [0, height -1 ],            # Bottom-left corner
    [width - 1, height  -1 ]  ,  # Bottom-right corner
    [width - 1, 0],             # Top-right corner
    ], dtype=np.float32)
    
    homography_matrix = cv.getPerspectiveTransform(source_points, destination_points)
    warped_image = cv.warpPerspective(image, homography_matrix, (width, height))
    return warped_image


##################################################################################################


def kernal_inbetween(k_image, gaussian_kernel, segments):
    #step inbetween 
    horizontal_steps = segments*0.4
    vertical_steps = segments*0.3
    colors = []
    
    ptA = (0, 0)
    ptB = (640-1, 0)
    ptC = (0, 480-1)
    ptD = (640-1, 480-1)

    #A to C 
    for step in range (int(vertical_steps + 1)):
        point_x = int(ptA[0] + step * (ptC[0] - ptA[0]) / vertical_steps)
        point_y = int(ptA[1] + step * (ptC[1] - ptA[1]) / vertical_steps)
        kernel_output = cv.filter2D(k_image, -1, gaussian_kernel)[point_y, point_x]
        colors.append(kernel_output)  
    #A to B
    for step in range(int(horizontal_steps + 1)):
        point_x = int(ptA[0] + step * (ptB[0] - ptA[0]) / horizontal_steps)
        point_y = int(ptA[1] + step * (ptB[1] - ptA[1]) / horizontal_steps)
        kernel_output = cv.filter2D(k_image, -1, gaussian_kernel)[point_y, point_x]
        colors.append(kernel_output)  

    #B to D
    for step in range(int(vertical_steps + 1)):
        point_x = int(ptB[0] + step * (ptD[0] - ptB[0]) / vertical_steps)
        point_y = int(ptB[1] + step * (ptD[1] - ptB[1]) / vertical_steps)
        kernel_output = cv.filter2D(k_image, -1, gaussian_kernel)[point_y, point_x]
        colors.append(kernel_output)  

    return colors

##################################################################################################

def get_colors_inbetween(k_image, step, segments=60):
    horizontal_steps = int(segments*0.4)
    vertical_steps = int(segments*0.3)
    colors = []
    

    ptA = (0 + step, 0 + step)
    ptB = (640 - step, 0 + step)
    ptC = (0 + step, 480-step)
    ptD = (640-step, 480-step)

    for step in range(vertical_steps + 1):
        point_x = int(ptA[0] + step * (ptC[0] - ptA[0]) / vertical_steps)
        point_y = int(ptA[1] + step * (ptC[1] - ptA[1]) / vertical_steps)
        colors.append(k_image[point_y, point_x])  

    for step in range(horizontal_steps + 1):
        point_x = int(ptA[0] + step * (ptB[0] - ptA[0]) / horizontal_steps)
        point_y = int(ptA[1] + step * (ptB[1] - ptA[1]) / horizontal_steps)
        colors.append(k_image[point_y, point_x]) 

    for step in range(vertical_steps + 1):
        point_x = int(ptB[0] + step * (ptD[0] - ptB[0]) / vertical_steps)
        point_y = int(ptB[1] + step * (ptD[1] - ptB[1]) / vertical_steps)
        colors.append(k_image[point_y, point_x]) 
    return colors
        
##################################################################################################


def draw_color_line(colors, image_width=500, image_height=100, output_path="output.png"):
    image = np.ones((image_height, image_width, 3), dtype=np.uint8) * 255
    colors = [tuple(map(int, color)) for color in colors]
    num_colors = len(colors)
    step = image_width // num_colors if num_colors > 0 else 1

    for i in range(num_colors - 1):
        start_x = i * step
        end_x = (i + 1) * step
        color = colors[i]
        color = [(abs(255 - c)) for c in color]
        cv.line(image, (start_x, image_height // 2), (end_x, image_height // 2), color, thickness=2)

    cv.imshow('line', image)
    print(f"Image saved to {output_path}")


##################################################################################################


def average_colors(colors, window_size=3):
    if window_size % 2 == 0 or window_size < 1:
        raise ValueError("Window size must be a positive odd integer.")
    half_window = window_size // 2
    num_colors = len(colors)
    averaged_colors = []
    for i in range(num_colors):
        start = max(0, i - half_window)
        end = min(num_colors, i + half_window + 1)
        window = colors[start:end]
        average = np.mean(window, axis=0).astype(np.uint8)  # Ensure result is uint8
        averaged_colors.append(average)

    return averaged_colors

##################################################################################################

def contour_images(image):

    if image is None:
        print("Error: Could not load image.")
        exit()
        
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    edges = cv.Canny(gray, 50, 150)
    contours, _ = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    points = []

    if not contours:
        print("No contours found in the image.")
        return None

    if contours:
        largest_contour = max(contours, key=cv.contourArea)

        epsilon = 0.02 * cv.arcLength(largest_contour, True)
        approx = cv.approxPolyDP(largest_contour, epsilon, True)
        if len(approx) == 4:
            corners = approx.reshape(-1, 2) 

            corners = sorted(corners, key=lambda p: p[1])
            top_points = sorted(corners[:2], key=lambda p: p[0])
            bottom_points = sorted(corners[2:], key=lambda p: p[0])

            for point in approx:
                print(f"{tuple(point[0])}")
                points.append(point)
                
                top_left, top_right = top_points
                bottom_left, bottom_right = bottom_points

                # show contour lines for each image
                image = draw_line(image, top_left, top_right)
                image = draw_line(image, top_right, bottom_right)
                image = draw_line(image, bottom_right, bottom_left)
                image = draw_line(image, top_left, bottom_left)

                return top_left, bottom_left, bottom_right, top_right
        else:
            print(f"Detected contour does not have 4 corners. Found {len(approx)} corners.")
        return None
    
    cv.imshow('Screen Detection', image)
    cv.waitKey(100)
    cv.destroyAllWindows()

##################################################################################################


def show_video(images,title):
    for image in images:
            cv.imshow(title, image) 
            key = cv.waitKey(300)  # Wait for 300 ms for the next frame
            if key == 27:  # Exit if 'ESC' is pressed
                break
    cv.destroyAllWindows()


##################################################################################################

# show a video folder of frames, then show the corresponding output warped images
def play_video_folder():

    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Specify the image folder that you want to use and specify type, ex: .png, .jpg, etc.
    image_path = os.path.join(script_dir, 'rgb_images')
    images_list = glob.glob(os.path.join(image_path, '*.png'))

    images = [cv.imread(i) for i in images_list]  # Example frames
    
    warped_images_list = []

    # loop through each image frame in images 'video' folder
    for image in images:

        try:
            corners = contour_images(image)
            if corners is None:
                # print(f"Skipping image due to invalid contour.")
                continue

            top_left, bottom_left, bottom_right, top_right = corners

            warped_image = perspective_warp(top_left, bottom_left, bottom_right, top_right, image)

            warped_images_list.append(warped_image)

        except ValueError as e:
            print(f"Error processing image: {e}")
            continue

    # extract the color data from edges of each image
    show_video(images, "Video Playback")

    # show the warped color from the top edge of the computer
    show_video(warped_images_list, "Warped Images")

##################################################################################################

def detectScreen(frame):
    corners = contour_images(frame)
    if corners is None:
        print(f"Skipping image due to invalid contour.")
        
    return corners


##################################################################################################

def RT_screen_cam(kernel_size, display_type):
    x = 0
    print("Starting webcam initialization...")
    cap = cv.VideoCapture(0, cv.CAP_DSHOW)

    if not cap.isOpened():
        print("Failed to open camera.\n")
        exit()

    print("Camera opened successfully.\n")
    print("Starting to capture frames...")

    # flag determining screen corners found
    corners_detected = 0

    # arbitrary counter to ensure consistent corner points found
    counter = 0

    # segments represents number of LEDs
    segments = 60
    
    g_1 = scipy.signal.windows.gaussian(kernel_size, std=1)

    try:
        # connect to desired serial port and set baud rate
        ser = serial.Serial("COM6", 115200, timeout=1)
        time.sleep(2)  
        print(f"Connected to {ser.name}.")

    except serial.SerialException as e:
        print(f"Serial error: {e}")

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Retrying...")
            continue
        cv.imshow('frame', frame)

        try:
            # wait 50 counter iterations to determine corners, when found, set flag, warp and extract color
            if not corners_detected and counter < 50:
                corners = detectScreen(frame)
                # show contour results after 50 loops
                # cv.imshow('frame', frame)
                if cv.waitKey(1) == ord('q'):
                    print("Exiting capture loop.")
                    break
            if counter == 50:
                corners_detected = 1
            if corners_detected and counter > 50:
                top_left, bottom_left, bottom_right, top_right = corners
                warped_image = perspective_warp(top_left, bottom_left, bottom_right, top_right, frame)
                # wait 10 ms for each frame, lower wait times cause LED flickering
                if cv.waitKey(10) == ord('q'):
                    print("Exiting capture loop.")
                    break

                warped_image_rgb = cv.cvtColor(warped_image, cv.COLOR_BGR2RGB)
                if (kernel_size == 0):
                    color_array = np.array(get_colors_inbetween(warped_image_rgb, step= 5, segments=segments))
                else:
                    color_array = np.array(kernal_inbetween(warped_image_rgb, g_1, segments))

                # if display type is 0 (default), average the colors, otherwise use individual color per LED
                if display_type == 0:
                    color_array = average_colors(color_array) # average colors along edges using desired window size

                flattened = list(np.concatenate(color_array))

                send_buf = [segments] + flattened + [9999]
                send_str = ','.join(map(str, send_buf))
                
                # send color data across serial data to micrcontroller
                if ser and ser.is_open:     
                    # print(f"Sent {x} : {send_str}")
                    x += 1
                    sendCommand(ser, send_str)
                else:
                    print("FAILED TO SEND CMD")
            # when counter reaches 50, confirm screen detection
            counter += 1
        except ValueError as e:
            print(f"Error processing image: {e}")
            continue
    # When everything done, release the capture
    cap.release()
    cv.destroyAllWindows()
    print("Camera released, program ended.")

##################################################################################################


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="AmbientSync")
    parser.add_argument("--kernel_size", type=int, help="color kernel size", default=0)
    parser.add_argument("--display_type", type=int, help="avg color across LEDs or color individual LEDs", default=0)
    args = parser.parse_args()

    RT_screen_cam(args.kernel_size, args.display_type)

    # play_video_folder()

    
##################################################################################################