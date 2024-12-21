import cv2
import numpy as np

# Create the screen size
screen_res = (3840, 2160)  # Adjust this to your screen resolution

# Define colors (white, red, green, blue)
colors = [
    np.full((screen_res[1], screen_res[0], 3), fill_value=(255, 255, 255), dtype=np.uint8),  # White
    np.full((screen_res[1], screen_res[0], 3), fill_value=(0, 0, 255), dtype=np.uint8),      # Red
    np.full((screen_res[1], screen_res[0], 3), fill_value=(0, 255, 0), dtype=np.uint8),      # Green
    np.full((screen_res[1], screen_res[0], 3), fill_value=(255, 0, 0), dtype=np.uint8)       # Blue
]

# Initialize the color index (starts with white)
color_index = 0

# Create a named window and set it to fullscreen
cv2.namedWindow("Color Screen", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Color Screen", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Display the initial white screen
while True:
    # Show the current color
    cv2.imshow("Color Screen", colors[color_index])

    # Wait for a key event
    key = cv2.waitKey(1) & 0xFF

    # Change color on Enter (ASCII code 13)
    if key == 13:  # Enter key
        color_index = (color_index + 1) % len(colors)

    # Break the loop on pressing 'q'
    if key == ord('q'):
        break

cv2.destroyAllWindows()
