import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
import os

# not using this but keeping for reference
def closest_point(points, target):
    """
    Finds the point closest to the target point.

    Parameters:
        points (list): List of numpy arrays where each element is a point [array([[x, y]], dtype=int32)].
        target (tuple): The target point as a tuple (x, y).

    Returns:
        tuple: The point in the list closest to the target point.
    """
    # Initialize the minimum distance to a large number
    min_distance = float('inf')
    closest_point = None
    for p in points:
        # Extract the x and y coordinates of the point
        point = tuple(p[0])  # Convert numpy array to tuple
        x1, y1 = point
        x2, y2 = target
        
        # Calculate the Euclidean distance
        distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        
        # Update the closest point if this one is closer
        if distance < min_distance:
            min_distance = distance
            closest_point = point

    return closest_point

# not using this but keeping for reference
def find_corners(points):
    
    if len(points) != 4:
        raise ValueError("You must provide exactly 4 points.")
    top_left = closest_point(points, (0,0))
    top_right = closest_point(points, (640,0))
    bottom_left = closest_point(points, (0,480))
    bottom_right = closest_point(points, (640,480))

    return top_left, top_right, bottom_left, bottom_right

def euclidean_distance(point1, point2):
    distance = np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point1[1]) ** 2)  
    return distance  

def draw_line(image, point1, point2, color=(0, 255, 0), thickness=2):
    cv.line(image, point1, point2, color, thickness)
    return image

def perspective_warp(pt_A, pt_B, pt_C, pt_D):    
    source_points = np.array([pt_A, pt_B, pt_C, pt_D], dtype=np.float32)
    # hardcoded
    # width = 640
    # height = 480

    width_top = euclidean_distance(top_left, top_right)
    width_bottom = euclidean_distance(bottom_left, bottom_right)
    width = int(max(width_top, width_bottom))

     # calculate the desired height
    height_right = euclidean_distance(top_right, bottom_right)
    height_left = euclidean_distance(top_left, bottom_left)
    height = int(max(height_left, height_right))

    destination_points = np.array([
    [0, 0],                     # Top-left corner
    [0, height -1 ],            # Bottom-left corner
    [width - 1, height  -1 ]  ,   # Bottom-right corner
    [width - 1, 0],             # Top-right corner
    ], dtype=np.float32)
    
    homography_matrix = cv.getPerspectiveTransform(source_points, destination_points)
    print(homography_matrix)
    warped_image = cv.warpPerspective(image, homography_matrix, (width, height))
    cv.imshow('Warped Image', warped_image)
    cv.waitKey(0)
    cv.destroyAllWindows()
    
def line_properties(pt1, pt2):
    if pt1[0] == pt2[0]:  # Vertical line
        return None, pt1[0]  # Slope is undefined, x-intercept is the x-coordinate
    slope = (pt2[1] - pt1[1]) / (pt2[0] - pt1[0])
    intercept = pt1[1] - slope * pt1[0]
    return slope, intercept
    
def get_colors_inbetween(ptA, ptB, ptC, ptD, segments=60):
    horizontal_steps = int(segments*0.4)
    vertical_steps = int(segments*0.3)
    colors = []
    
    for step in range(vertical_steps + 1):
        point_x = int(ptA[0] + step * (ptC[0] - ptA[0]) / vertical_steps)
        point_y = int(ptA[1] + step * (ptC[1] - ptA[1]) / vertical_steps)
        colors.append(image[point_y, point_x])  

    for step in range(horizontal_steps + 1):
        point_x = int(ptA[0] + step * (ptB[0] - ptA[0]) / horizontal_steps)
        point_y = int(ptA[1] + step * (ptB[1] - ptA[1]) / horizontal_steps)
        colors.append(image[point_y, point_x]) 

    for step in range(vertical_steps + 1):
        point_x = int(ptB[0] + step * (ptD[0] - ptB[0]) / vertical_steps)
        point_y = int(ptB[1] + step * (ptD[1] - ptB[1]) / vertical_steps)
        colors.append(image[point_y, point_x]) 
    return colors
        
def draw_color_line(colors, image_width=500, image_height=100, output_path="output.png"):
    image = np.ones((image_height, image_width, 3), dtype=np.uint8) * 255
    colors = [tuple(map(int, color)) for color in colors]
    num_colors = len(colors)
    step = image_width // num_colors if num_colors > 0 else 1

    for i in range(num_colors - 1):
        start_x = i * step
        end_x = (i + 1) * step
        color = colors[i]
        cv.line(image, (start_x, image_height // 2), (end_x, image_height // 2), color, thickness=2)

    cv.imwrite(output_path, image)
    print(f"Image saved to {output_path}")

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

# # Get the directory where the current script is located
# script_dir = os.path.dirname(os.path.abspath(__file__))

# # Probably need to change this, but code your own path!
# image_path = os.path.join(script_dir, 'capture_1731877075.png')
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the image file
image_path = os.path.join(script_dir, 'frames/sunsetimg_1.jpg')
print(image_path)

image = cv.imread(image_path) 

if image is None:
    print("Error: Could not load image.")
    exit()
    
gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
edges = cv.Canny(gray, 50, 150)
contours, _ = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
points = []

if contours:
    largest_contour = max(contours, key=cv.contourArea)

    epsilon = 0.02 * cv.arcLength(largest_contour, True)
    approx = cv.approxPolyDP(largest_contour, epsilon, True)
    corners = approx.reshape(-1, 2) 

    corners = sorted(corners, key=lambda p: p[1])
    top_points = sorted(corners[:2], key=lambda p: p[0])
    bottom_points = sorted(corners[2:], key=lambda p: p[0])

    for point in approx:
        print(f"{tuple(point[0])}")
        points.append(point)
        
    if len(approx) == 4:
        top_left, top_right = top_points
        bottom_left, bottom_right = bottom_points
        # image = draw_line(image, top_left, top_right)
        # image = draw_line(image, top_right, bottom_right)
        # image = draw_line(image, bottom_right, bottom_left)
        # image = draw_line(image, top_left, bottom_left)

cv.imshow('Screen Detection', image)
cv.waitKey(0)
cv.destroyAllWindows()

perspective_warp(top_left, bottom_left, bottom_right, top_right)
color_array = get_colors_inbetween(top_left, top_right, bottom_left, bottom_right)

avg_color = average_colors(color_array)

draw_color_line(avg_color)