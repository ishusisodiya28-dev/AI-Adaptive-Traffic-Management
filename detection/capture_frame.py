import cv2

cap = cv2.VideoCapture("videos/traffic.mp4")

cap.set(cv2.CAP_PROP_POS_MSEC, 5000)

success, frame = cap.read()

if success:
    cv2.imwrite("results/road_frame.jpg", frame)
    print("Road frame saved successfully!")
else:
    print("Frame not captured!")

cap.release()