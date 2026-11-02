
import cv2

image = cv2.imread("results/road_frame.jpg")

if image is None:
    print("Road frame not found!")
    exit()

# Approximate queue zones for this intersection
zones = {
    "LEFT APPROACH": [
        (100, 320), (650, 320), (780, 510), (100, 550)
    ],

    "CENTRE APPROACH": [
        (650, 280), (1250, 280), (1300, 500), (750, 520)
    ],

    "RIGHT APPROACH": [
        (1300, 300), (1900, 300), (1900, 560), (1350, 520)
    ]
}

for name, points in zones.items():
    polygon = points
    cv2.polylines(
        image,
        [__import__("numpy").array(polygon)],
        True,
        (0, 255, 0),
        3
    )

    x, y = points[0]
    cv2.putText(
        image,
        name,
        (x, y - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

cv2.imwrite("results/queue_zones_preview.jpg", image)

print("Queue zones marked successfully!")
