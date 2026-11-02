
from ultralytics import YOLO
import cv2
import math

model = YOLO("yolo11n.pt")
cap = cv2.VideoCapture("videos/traffic.mp4")

previous_positions = {}
stationary_frames = {}

MOVEMENT_THRESHOLD = 3
WAITING_LIMIT = 15

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
    moving = 0
    waiting = 0

    boxes = results[0].boxes

    if boxes is not None and boxes.id is not None:
        ids = boxes.id.cpu().numpy().astype(int)
        coordinates = boxes.xywh.cpu().numpy()

        for vehicle_id, box in zip(ids, coordinates):
            x, y = float(box[0]), float(box[1])

            if vehicle_id in previous_positions:
                old_x, old_y = previous_positions[vehicle_id]

                distance = math.hypot(x - old_x, y - old_y)

                if distance < MOVEMENT_THRESHOLD:
                    stationary_frames[vehicle_id] = (
                        stationary_frames.get(vehicle_id, 0) + 1
                    )
                else:
                    stationary_frames[vehicle_id] = 0

            else:
                stationary_frames[vehicle_id] = 0

            previous_positions[vehicle_id] = (x, y)

            if stationary_frames[vehicle_id] >= WAITING_LIMIT:
                waiting += 1
                status = "WAITING"
            else:
                moving += 1
                status = "MOVING"

            cv2.putText(
                output,
                status,
                (int(x), int(y)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255) if status == "WAITING" else (0, 255, 0),
                2
            )

    cv2.putText(output, f"Moving: {moving}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.putText(output, f"Waiting: {waiting}", (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    cv2.imshow("Traffic Flow Analysis", output)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
