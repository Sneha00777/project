"""
PhysioVision - Yoga Pose Accuracy Detector
CLOUD-DEPLOYABLE version using streamlit-webrtc.

Unlike App2.py (which grabs the webcam directly on the machine running the
server via cv2.VideoCapture(0) — only works when running locally), this
version captures video from the USER'S BROWSER via WebRTC and streams it to
the server for processing. This is what allows it to work when deployed on
Streamlit Community Cloud (or any other host) instead of only on your laptop.
"""

import os
import sys
import queue

import av
import cv2
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# ---------------------------------------------------------------------------
# Make backend/ importable (same setup as App2.py)
# ---------------------------------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_PATH = os.path.abspath(os.path.join(CURRENT_DIR, "..", "backend"))

if BACKEND_PATH not in sys.path:
    sys.path.insert(0, BACKEND_PATH)

# PoseDetector loads its model using a relative path, so we need the
# working directory to be backend/ for it to find pose_landmarker.task
os.chdir(BACKEND_PATH)

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
st.caption(
    "Live browser-webcam pose detection with real-time accuracy scoring "
    "and feedback. Works locally and when deployed."
)


# ---------------------------------------------------------------------------
# Cached backend objects
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

st.sidebar.markdown("---")
st.sidebar.caption(
    "Click **Start** below the video, allow camera access in your browser, "
    "then stand back so your full body is visible."
)

# A thread-safe queue used to pass the latest score data from the WebRTC
# video-processing thread (recv) back to the main Streamlit thread for display.
result_queue: "queue.Queue" = queue.Queue(maxsize=1)


# ---------------------------------------------------------------------------
# Video frame callback — runs once per incoming browser frame
# ---------------------------------------------------------------------------
def video_frame_callback(frame: av.VideoFrame) -> av.VideoFrame:
    img = frame.to_ndarray(format="bgr24")
    img = cv2.flip(img, 1)

    # --- Module 1: landmark detection ---
    landmarks = detector.detect(img)

    # --- Module 2/3: accuracy scoring ---
    raw_pose_data = metrics.analyze(
        landmark_data=landmarks,
        target_pose=target_pose,
    )

    if landmarks is not None:
        img = detector.draw_landmarks(img)

    # Push latest result to the main thread (non-blocking; drop if full)
    try:
        result_queue.put_nowait(raw_pose_data)
    except queue.Full:
        try:
            result_queue.get_nowait()
        except queue.Empty:
            pass
        result_queue.put_nowait(raw_pose_data)

    return av.VideoFrame.from_ndarray(img, format="bgr24")


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
video_col, stats_col = st.columns([2, 1])

with video_col:
    # Public STUN server so WebRTC can establish a connection from the
    # browser to the server even across networks/NAT.
    RTC_CONFIGURATION = RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )

    webrtc_ctx = webrtc_streamer(
        key="physiovision",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION,
        video_frame_callback=video_frame_callback,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

with stats_col:
    st.subheader("Live Accuracy")
    score_placeholder = st.empty()
    status_placeholder = st.empty()
    message_placeholder = st.empty()
    angles_placeholder = st.empty()

    if webrtc_ctx.state.playing:
        import time

        while True:
            try:
                raw_pose_data = result_queue.get(timeout=1.0)
            except queue.Empty:
                continue

            score = raw_pose_data.get("score", 0)
            is_correct = raw_pose_data.get("is_correct", False)
            message = raw_pose_data.get("message", "")
            angles = raw_pose_data.get("angles", {})

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

            if not webrtc_ctx.state.playing:
                break
    else:
        frame_note = "Camera is stopped. Click **Start** above the video to begin."
        score_placeholder.info(frame_note)