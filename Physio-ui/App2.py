"""
PhysioVision - Yoga Pose Accuracy Detector
Streamlit frontend integrated with backend (Module 1 + 2 + 3)
"""

import os
import sys
import time

import cv2
import streamlit as st

# ---------------------------------------------------------------------------
# Make backend/ importable.
# This file lives at Physio-ui/App2.py, backend/ is a sibling folder:
#   repo_root/
#     Physio-ui/App2.py   <-- this file
#     backend/...
# If your actual layout differs, just fix BACKEND_PATH below.
# ---------------------------------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_PATH = os.path.abspath(os.path.join(CURRENT_DIR, "..", "backend"))

if BACKEND_PATH not in sys.path:
    sys.path.insert(0, BACKEND_PATH)
    os.chdir(BACKEND_PATH)

# --- Backend imports (Module 1 & 2, unchanged) ---
from vision.pose_detector import PoseDetector          # noqa: E402
from metrices.metrices import Metrics                  # noqa: E402
from metrices.pose_database import get_all_poses       # noqa: E402


# ---------------------------------------------------------------------------
# Streamlit page setup
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="PhysioVision - Yoga Pose Detector",
    page_icon="🧘",
    layout="wide",
)

st.title("🧘 PhysioVision — Real-Time Yoga Pose Accuracy Detector")
st.caption("Live webcam pose detection with real-time accuracy scoring and feedback.")


# ---------------------------------------------------------------------------
# Session state (persists across Streamlit reruns)
# ---------------------------------------------------------------------------
if "running" not in st.session_state:
    st.session_state.running = False


# ---------------------------------------------------------------------------
# Cached backend objects — created once, reused across reruns
# (avoids reloading the mediapipe model every frame)
# ---------------------------------------------------------------------------
@st.cache_resource
def load_detector():
    return PoseDetector()


@st.cache_resource
def load_metrics():
    return Metrics()


detector = load_detector()
metrics = load_metrics()


# ---------------------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------------------
st.sidebar.header("Controls")

available_poses = get_all_poses()
target_pose = st.sidebar.selectbox(
    "Select target pose",
    options=available_poses,
    index=available_poses.index("tree_pose") if "tree_pose" in available_poses else 0,
)

col_start, col_stop = st.sidebar.columns(2)
start_clicked = col_start.button("▶ Start", use_container_width=True)
stop_clicked = col_stop.button("⏹ Stop", use_container_width=True)

if start_clicked:
    st.session_state.running = True
if stop_clicked:
    st.session_state.running = False

st.sidebar.markdown("---")
st.sidebar.caption(
    "Stand in front of your webcam, pick a target pose, and press Start. "
    "Score updates live as you hold the pose."
)


# ---------------------------------------------------------------------------
# Layout: video on the left, live stats on the right
# ---------------------------------------------------------------------------
video_col, stats_col = st.columns([2, 1])

with video_col:
    frame_placeholder = st.empty()

with stats_col:
    st.subheader("Live Accuracy")
    score_placeholder = st.empty()
    status_placeholder = st.empty()
    message_placeholder = st.empty()
    angles_placeholder = st.empty()


def render_stats(pose_data):
    """Push the latest raw_pose_data from Module 2/3 into the UI."""
    score = pose_data.get("score", 0)
    is_correct = pose_data.get("is_correct", False)
    message = pose_data.get("message", "")
    angles = pose_data.get("angles", {})

    score_placeholder.metric("Accuracy Score", f"{score}%")

    if is_correct:
        status_placeholder.success("✅ Correct Form")
    else:
        status_placeholder.warning("⚠️ Needs Adjustment")

    message_placeholder.info(message if message else "—")

    if angles:
        angles_placeholder.table(
            {
                "Joint": list(angles.keys()),
                "Angle (°)": [round(v, 1) for v in angles.values()],
            }
        )
    else:
        angles_placeholder.empty()


# ---------------------------------------------------------------------------
# Main capture loop
# ---------------------------------------------------------------------------
def run_camera_loop():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        st.error("Could not open webcam. Check that no other app is using it.")
        st.session_state.running = False
        return

    try:
        while st.session_state.running:
            success, frame = cap.read()

            if not success:
                st.error("Failed to capture frame from webcam.")
                break

            frame = cv2.flip(frame, 1)

            # --- Module 1: landmark detection ---
            landmarks = detector.detect(frame)

            # --- Module 2/3: accuracy scoring ---
            raw_pose_data = metrics.analyze(
                landmark_data=landmarks,
                target_pose=target_pose,
            )

            # Draw skeleton overlay if a person is detected
            if landmarks is not None:
                frame = detector.draw_landmarks(frame)

            # Convert BGR (OpenCV) -> RGB (Streamlit/PIL expects RGB)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(rgb_frame, channels="RGB", use_container_width=True)

            render_stats(raw_pose_data)

            # Small delay to avoid pegging the CPU; also lets Streamlit
            # process the Stop button click in between frames.
            time.sleep(0.03)

    finally:
        cap.release()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if st.session_state.running:
    run_camera_loop()
else:
    frame_placeholder.info("Camera is stopped. Press **Start** in the sidebar to begin.")