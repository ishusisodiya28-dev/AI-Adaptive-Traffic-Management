
from ultralytics import YOLO
import cv2
import numpy as np

model = YOLO("yolo11n.pt")
cap = cv2.VideoCapture("videos/traffic.mp4")

zones = {
    "LEFT": np.array([
        (100, 320), (650, 320), (780, 510), (100, 550)
    ]),
    "CENTRE": np.array([
        (650, 280), (1250, 280), (1300, 500), (750, 520)
    ]),
    "RIGHT": np.array([
        (1300, 300), (1900, 300), (1900, 560), (1350, 520)
    ])
}

previous_positions = {}
stationary_frames = {}

WAITING_LIMIT = 15
VEHICLE_CLASSES = [2, 3, 5, 7]

while cap.isOpened():

    success, frame = cap.read()
    if not success:
        break

    results = model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml",
        conf=0.35,
        verbose=False
    )

    output = results[0].plot()

    queue_counts = {
        "LEFT": 0,
        "CENTRE": 0,
        "RIGHT": 0
    }

    boxes = results[0].boxes

    if boxes is not None and boxes.id is not None:

        ids = boxes.id.cpu().numpy().astype(int)
        classes = boxes.cls.cpu().numpy().astype(int)
        coordinates = boxes.xywh.cpu().numpy()

        for vehicle_id, cls, box in zip(ids, classes, coordinates):

            if cls not in VEHICLE_CLASSES:
                continue

            x, y = int(box[0]), int(box[1])

            if vehicle_id in previous_positions:
                old_x, old_y = previous_positions[vehicle_id]

                distance = np.hypot(x - old_x, y - old_y)

                if distance < 3:
                    stationary_frames[vehicle_id] = (
                        stationary_frames.get(vehicle_id, 0) + 1
                    )
                else:
                    stationary_frames[vehicle_id] = 0
            else:
                stationary_frames[vehicle_id] = 0

            previous_positions[vehicle_id] = (x, y)

            if stationary_frames[vehicle_id] >= WAITING_LIMIT:

                for zone_name, polygon in zones.items():

                    inside = cv2.pointPolygonTest(
                        polygon, (x, y), False
                    )

                    if inside >= 0:
                        queue_counts[zone_name] += 1

    for zone_name, polygon in zones.items():

        cv2.polylines(
            output, [polygon], True, (0, 255, 0), 3
        )

    y_position = 40

    for zone_name, count in queue_counts.items():

        if count < 5:
            congestion = "LOW"
        elif count < 12:
            congestion = "MEDIUM"
        else:
            congestion = "HIGH"

        text = f"{zone_name}: Queue {count} | {congestion}"

        cv2.putText(
            output,
            text,
            (20, y_position),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

        y_position += 35

    cv2.imshow("AI Traffic Queue Analysis", output)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
