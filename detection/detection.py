
from ultralytics import YOLO
import cv2

# Load YOLO11 pretrained model
model = YOLO("yolo11n.pt")

# Open traffic video
cap = cv2.VideoCapture("videos/traffic.mp4")

if not cap.isOpened():
    print("Error: Traffic video not found!")
    exit()

while True:
    success, frame = cap.read()

    if not success:
        break

    # Detect and track vehicles
    results = model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml",
        conf=0.35,
        verbose=False
    )

    # Display detection and tracking IDs
    output = results[0].plot()

    cv2.imshow("AI Traffic Detection - YOLO11 + ByteTrack", output)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
