
import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO
from pathlib import Path

st.set_page_config(
    page_title="AI Camera Traffic Analysis",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 AI Camera-Based Traffic Analysis")
st.caption("YOLO11 + ByteTrack | Vehicle Tracking and Queue Detection")

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
VIDEO_PATH = BASE_DIR / "videos" / "traffic.mp4"
MODEL_PATH = BASE_DIR / "yolo11n.pt"

if not VIDEO_PATH.exists():
    st.error(f"Video not found: {VIDEO_PATH}")
    st.stop()

if not MODEL_PATH.exists():
    st.error(f"YOLO model not found: {MODEL_PATH}")
    st.stop()

WAITING_LIMIT = 15
VEHICLE_CLASSES = [2, 3, 5, 7]

# Load model only when needed
@st.cache_resource
def load_model(model_path):
    return YOLO(str(model_path))

st.info("Video source: recorded traffic video")

if st.button("▶ Start Camera Video Analysis", type="primary"):

    frame_area = st.empty()
    status_area = st.empty()
    progress_area = st.progress(0)

    previous_positions = {}
    stationary_frames = {}

    latest_counts = {
        "LEFT": 0,
        "CENTRE": 0,
        "RIGHT": 0
    }

    try:
        with st.spinner("Loading YOLO model..."):
            model = load_model(MODEL_PATH)

        cap = cv2.VideoCapture(str(VIDEO_PATH))

        if not cap.isOpened():
            st.error("Unable to open traffic video.")
            st.stop()

        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if frame_count <= 0:
            st.error("Video contains no readable frames.")
            cap.release()
            st.stop()

        ret, first_frame = cap.read()

        if not ret:
            st.error("Unable to read first video frame.")
            cap.release()
            st.stop()

        height, width = first_frame.shape[:2]

        # Scale zones according to video dimensions
        sx = width / 1920
        sy = height / 1080

        def scale_polygon(points):
            return np.array([
                (int(x * sx), int(y * sy))
                for x, y in points
            ], dtype=np.int32)

        zones = {
            "LEFT": scale_polygon([
                (100, 320), (650, 320),
                (780, 510), (100, 550)
            ]),
            "CENTRE": scale_polygon([
                (650, 280), (1250, 280),
                (1300, 500), (750, 520)
            ]),
            "RIGHT": scale_polygon([
                (1300, 300), (1900, 300),
                (1900, 560), (1350, 520)
            ])
        }

        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        processed = 0

        while cap.isOpened():

            success, frame = cap.read()

            if not success:
                break

            results = model.track(
                frame,
                persist=True,
                tracker="bytetrack.yaml",
                conf=0.35,
                classes=VEHICLE_CLASSES,
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
                coordinates = boxes.xywh.cpu().numpy()

                for vehicle_id, box in zip(ids, coordinates):

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
                            if cv2.pointPolygonTest(
                                polygon, (x, y), False
                            ) >= 0:
                                queue_counts[zone_name] += 1

            # Draw zones and queue information
            for zone_name, polygon in zones.items():

                cv2.polylines(
                    output, [polygon], True, (0, 255, 0), 3
                )

            y_position = 40

            for zone_name, count in queue_counts.items():

                congestion = (
                    "LOW" if count < 5
                    else "MEDIUM" if count < 12
                    else "HIGH"
                )

                cv2.putText(
                    output,
                    f"{zone_name}: Queue {count} | {congestion}",
                    (20, y_position),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2
                )

                y_position += 35

            # Resize only for dashboard display
            display_width = 960
            display_height = int(
                output.shape[0] * display_width / output.shape[1]
            )

            display_frame = cv2.resize(
                output, (display_width, display_height)
            )

            # Update dashboard every 2 frames
            if processed % 2 == 0:
                frame_area.image(
                    cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB),
                    channels="RGB",
                    use_container_width=True
                )

                status_area.write(
                    f"Processing: {processed + 1} / {frame_count} frames"
                )

                progress_area.progress(
                    min((processed + 1) / frame_count, 1.0)
                )

            latest_counts = queue_counts
            processed += 1

        cap.release()

        progress_area.progress(1.0)
        status_area.success(f"Analysis completed! Total frames: {processed}")

        st.subheader("Final Queue Analysis")

        cols = st.columns(3)

        for col, (zone, count) in zip(cols, latest_counts.items()):

            level = (
                "LOW" if count < 5
                else "MEDIUM" if count < 12
                else "HIGH"
            )

            col.metric(zone, count)
            col.write(f"Congestion: **{level}**")

        st.success("Traffic video analysis completed successfully!")

        st.info(
            "Queue counts represent stationary tracked vehicles "
            "in each zone in the final processed frame."
        )

    except Exception as error:
        st.error(f"Analysis failed: {error}")
