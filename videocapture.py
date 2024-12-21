import cv2 as cv
import numpy as np

def detect_screen_and_record(output_file='output.mp4', frame_width=640, frame_height=480, fps=30):
    cap = cv.VideoCapture(1, cv.CAP_DSHOW)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    fourcc = cv.VideoWriter_fourcc(*'XVID')  
    out = cv.VideoWriter(output_file, fourcc, fps, (frame_width, frame_height))

    print("Recording... Press 'q' to stop.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        edges = cv.Canny(gray, 50, 150)
        contours, _ = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        if contours:
            largest_contour = max(contours, key=cv.contourArea)
            epsilon = 0.02 * cv.arcLength(largest_contour, True)
            approx = cv.approxPolyDP(largest_contour, epsilon, True)

            if len(approx) == 4:  
                contour_image = cv.drawContours(frame, [approx], -1, (0, 255, 0), 3)
                combined = cv.hconcat([cv.cvtColor(edges, cv.COLOR_GRAY2BGR), contour_image])
                cv.imshow('Edges (left) vs Contours (right)', combined)
                cv.imwrite('output_edges.jpg', combined)

        cv.imshow("Webcam with Green Outline", frame)
        out.write(frame)

        # Stop recording if 'q' is pressed
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
        
    cap.release()
    out.release()
    cv.destroyAllWindows()
    print(f"Recording saved to {output_file}.")

if __name__ == "__main__":
    detect_screen_and_record()
