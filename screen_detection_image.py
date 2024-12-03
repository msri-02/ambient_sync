import cv2
import numpy as np

# Load the image
image = cv2.imread('C:/Users/prana/OneDrive/Calpoly/EE 428/Final Project/Object_Detection_Images/white.png')

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
        if mean_brightness > 200:  # Example threshold for detecting a white screen
            # Draw the rectangle (in white) on the mask
            cv2.drawContours(mask, [approx], -1, (255), thickness=cv2.FILLED)  # Fill the rectangle with white

# Show the mask
cv2.imshow("Mask with Detected Rectangles", mask)

cv2.waitKey(0)
cv2.destroyAllWindows()
