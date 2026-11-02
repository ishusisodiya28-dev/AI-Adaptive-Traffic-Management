from ultralytics import YOLO
import cv2

model = YOLO("yolo11n.pt")

cap = cv2.VideoCapture("videos/traffic.mp4")

vehicle_classes = {
    2: "Car",
    3: "Motorcycle",
    5: "Bus",
    7: "Truck"
}

total_vehicles = set()

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

    counts = {
        "Car": 0,
        "Motorcycle": 0,
        "Bus": 0,
        "Truck": 0
    }

    boxes = results[0].boxes

    if boxes is not None and boxes.id is not None:

        ids = boxes.id.cpu().numpy().astype(int)
        classes = boxes.cls.cpu().numpy().astype(int)

        for vehicle_id, cls in zip(ids, classes):

            if cls in vehicle_classes:
                vehicle_name = vehicle_classes[cls]

                counts[vehicle_name] += 1
                total_vehicles.add(vehicle_id)

    current_count = sum(counts.values())

    if current_count < 10:
        density = "LOW"
    elif current_count < 25:
        density = "MEDIUM"
    else:
        density = "HIGH"

    output = results[0].plot()

    cv2.putText(
        output,
        f"Vehicles: {current_count}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.putText(
        output,
        f"Density: {density}",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 255),
        2
    )

    cv2.imshow("Traffic Analysis", output)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

print("Unique vehicle IDs detected:", len(total_vehicles))

cap.release()
cv2.destroyAllWindows()