import cv2
import time

print("Starting webcam initialization...")

start = time.time()
# Attempt to open the camera
cap = cv2.VideoCapture(1)
elapsed_time = time.time() - start

if not cap.isOpened():
    print(f"Failed to open camera after {elapsed_time:.2f} seconds.")
    exit()

print(f"Camera opened successfully in {elapsed_time:.2f} seconds.")
print("Starting to capture frames...")

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Retrying...")
        continue  # Retry instead of exiting immediately

    print(f"Frame captured at {time.time():.2f} seconds")  # Log timestamp of each frame
    # Display the resulting frame
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) == ord('q'):
        print("Exiting capture loop.")
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
print("Camera released, program ended.")
