import cv2
import numpy as np
import os
import matplotlib.pyplot as plt

# Define the folder containing the images
image_folder = 'C:/Users/prana/OneDrive/Calpoly/EE 428/Final Project/Object_Detection_Images/'

# Get a list of all image files in the folder
image_files = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]

# Loop through all image files
for image_file in image_files:
    # Load the image
    image = cv2.imread(image_file)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Canny edge detection
    edges = cv2.Canny(gray, 50, 150)

    # Find contours
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create a black mask of the same size as the original image
    mask = np.zeros_like(gray)

    # Loop through the contours and filter for rectangles with brightness detection
    for contour in contours:
        # Approximate the contour by a polygon
        epsilon = 0.005 * cv2.arcLength(contour, True)  # Adjust epsilon to control approximation
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # If the contour has 4 vertices, it is likely a rectangle (screen)
        if len(approx) == 4:
            # Create a mask for the current contour
            contour_mask = np.zeros_like(gray)
            cv2.drawContours(contour_mask, [approx], -1, 255, thickness=cv2.FILLED)

            # Calculate the mean brightness inside the contour
            mean_brightness = cv2.mean(gray, mask=contour_mask)[0]

            # Filter based on brightness threshold (adjust as needed)
            if mean_brightness > 190:  # Example threshold for detecting a white screen
                # Draw the rectangle (in white) on the mask
                cv2.drawContours(mask, [approx], -1, (255), thickness=cv2.FILLED)  # Fill the rectangle with white

    # Convert the mask to a 3-channel image for side-by-side display
    mask_rgb = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    # Convert BGR to RGB for matplotlib compatibility
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mask_rgb = cv2.cvtColor(mask_rgb, cv2.COLOR_BGR2RGB)

    # Display the original image and the mask side by side
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.imshow(image_rgb)
    plt.title("Original Image")
    plt.axis("off")

    plt.subplot(1, 2, 2)
    plt.imshow(mask_rgb)
    plt.title("Mask")
    plt.axis("off")

    plt.show()
