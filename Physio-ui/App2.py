"""
AI Yoga Pose Correction — LIVE (real backend wired in)
=======================================================
This version calls the real PhysioVision backend (MediaPipe pose detection +
joint-angle scoring from backend/metrices) on every photo captured through
st.camera_input. If the backend fails to import for any reason (e.g. a
dependency didn't build on the host), the app falls back to demo mode
automatically instead of crashing.

Run locally:
    pip install -r requirements.txt
    streamlit run App2.py
"""

import os
import sys
import io
import random
import time
from datetime import datetime

import json
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
from PIL import Image

# ----------------------------------------------------------------------------
# WIRE UP THE REAL BACKEND (FIXED PATH LOOKUP)
# ----------------------------------------------------------------------------
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.abspath(os.path.join(_THIS_DIR, ".."))
_BACKEND_DIR = os.path.join(_ROOT_DIR, "backend")

for path in [_ROOT_DIR, _BACKEND_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

BACKEND_AVAILABLE = True
BACKEND_ERROR = ""
try:
    import cv2
    from backend.vision.pose_detector import PoseDetector
    from backend.metrices.metrices import Metrics
except Exception as e1:
    try:
        import cv2
        from vision.pose_detector import PoseDetector
        from metrices.metrices import Metrics
    except Exception as e2:
        BACKEND_AVAILABLE = False
        BACKEND_ERROR = f"Primary: {e1} | Secondary: {e2}"


@st.cache_resource(show_spinner="Loading pose model (first time only)...")
def get_pose_detector():
    return PoseDetector()


@st.cache_resource(show_spinner=False)
def get_metrics_engine():
    return Metrics()


def speak_in_browser(text: str) -> None:
    """Reads feedback aloud using the browser's built-in text-to-speech."""
    if not text:
        return
    safe_text = json.dumps(text)
    components.html(
        f"""
        <script>
            const msg = new SpeechSynthesisUtterance({safe_text});
            msg.rate = 1.0;
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(msg);
        </script>
        """,
        height=0,
    )


# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Yoga Pose Correction",
    page_icon="🧘",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# CUSTOM CSS
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(160deg, #0D0B14 0%, #17111F 55%, #140F1C 100%);
        }
        .main-header {
            font-size: 2.6rem;
            font-weight: 800;
            background: linear-gradient(90deg, #D8BFFF, #9D7FD1 60%, #7C5CBF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0;
            letter-spacing: 0.5px;
        }
        .sub-header {
            font-size: 1rem;
            color: #B8AFC9;
            margin-top: 0;
        }
        .card {
            background-color: #1A1625;
            border: 1px solid rgba(182, 156, 219, 0.25);
            border-radius: 16px;
            padding: 1.3rem 1.5rem;
            box-shadow: 0 4px 18px rgba(124, 92, 191, 0.18);
            margin-bottom: 1rem;
        }
        .pose-pill {
            display: inline-block;
            background-color: rgba(182, 156, 219, 0.16);
            color: #D8BFFF;
            border: 1px solid rgba(182, 156, 219, 0.35);
            padding: 4px 14px;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-right: 6px;
        }
        .tip-item {
            background-color: rgba(232, 132, 90, 0.12);
            border-left: 4px solid #E8845A;
            padding: 8px 12px;
            border-radius: 6px;
            margin-bottom: 8px;
            font-size: 0.92rem;
            color: #F3D9CB;
        }
        .good-item {
            background-color: rgba(76, 175, 125, 0.14);
            border-left: 4px solid #4CAF7D;
            padding: 8px 12px;
            border-radius: 6px;
            margin-bottom: 8px;
            font-size: 0.92rem;
            color: #CFEFDD;
        }
        .video-placeholder {
            background-color: #150E1F;
            border: 1px dashed rgba(182, 156, 219, 0.4);
            color: #C9BEDA;
            border-radius: 16px;
            height: 420px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            font-size: 1rem;
            padding: 1rem;
        }
        div[data-testid="stMetricValue"] {
            color: #D8BFFF;
        }
        .stButton>button {
            border-radius: 10px;
            font-weight: 600;
            box-shadow: 0 2px 12px rgba(124, 92, 191, 0.35);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# POSE DATA — display info + mapping to the real backend's pose_database keys
# ----------------------------------------------------------------------------
POSES = {
    "Tadasana (Mountain Pose)": {
        "emoji": "🧍",
        "difficulty": "Beginner",
        "description": "Stand tall, feet together, spine straight, shoulders relaxed.",
        "backend_key": "tadasana",
    },
    "Vrikshasana (Tree Pose)": {
        "emoji": "🌳",
        "difficulty": "Beginner",
        "description": "One foot on inner thigh, hands raised, balance on standing leg.",
        "backend_key": "tree_pose",
    },
    "Trikonasana (Triangle Pose)": {
        "emoji": "📐",
        "difficulty": "Intermediate",
        "description": "Wide-legged stance, one hand down to shin/floor, other reaching up.",
        "backend_key": "trikonasana",
    },
    "Bhujangasana (Cobra Pose)": {
        "emoji": "🐍",
        "difficulty": "Beginner",
        "description": "Lying on stomach, lift chest with hands, gentle backbend.",
        "backend_key": "cobra_pose",
    },
    "Virabhadrasana II (Warrior II)": {
        "emoji": "⚔️",
        "difficulty": "Intermediate",
        "description": "Wide stance, front knee bent 90°, arms extended parallel to floor.",
        "backend_key": "warrior_2",
    },
}

# ----------------------------------------------------------------------------
# SESSION STATE INIT
# ----------------------------------------------------------------------------
defaults = {
    "session_active": False,
    "start_time": None,
    "accuracy": 0,
    "reps": 0,
    "best_streak": 0,
    "current_streak": 0,
    "tips": [],
    "good_points": [],
    "history": [],
    "last_message": "",
    "overlay_image": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ----------------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🧘 Pose Settings")

    selected_pose = st.selectbox("Choose a pose", list(POSES.keys()))
    pose_info = POSES[selected_pose]

    st.markdown(
        f"""
        <div class="card">
            <div style="font-size: 2.5rem; text-align:center;">{pose_info['emoji']}</div>
            <div class="pose-pill">{pose_info['difficulty']}</div>
            <p style="margin-top:10px; font-size:0.9rem; color:#4A3B33;">{pose_info['description']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    show_skeleton = st.checkbox("Show skeleton overlay", value=True)

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("▶️ Start", use_container_width=True, type="primary"):
            st.session_state.session_active = True
            st.session_state.start_time = time.time()
    with col_b:
        if st.button("⏹️ Stop", use_container_width=True):
            st.session_state.session_active = False

    st.markdown("---")
    if BACKEND_AVAILABLE:
        st.caption("⚙️ Model status: 🟢 **Real backend connected** — MediaPipe + joint-angle scoring.")
    else:
        st.caption("⚙️ Model status: 🔴 **Backend unavailable** — running in demo mode.")
        with st.expander("Why?"):
            st.code(BACKEND_ERROR or "Unknown import error")

# ----------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------
st.markdown('<p class="main-header">AI Yoga Pose Correction</p>', unsafe_allow_html=True)
st.markdown(
    f'<p class="sub-header">Currently practicing: <b>{selected_pose}</b> &nbsp;|&nbsp; '
    f'Status: {"🟢 Session live" if st.session_state.session_active else "⚪ Not started"}</p>',
    unsafe_allow_html=True,
)
st.write("")

# ----------------------------------------------------------------------------
# MAIN LAYOUT — webcam feed (left) + feedback panel (right)
# ----------------------------------------------------------------------------
col_video, col_feedback = st.columns([1.3, 1])

with col_video:
    st.markdown("#### 📷 Camera Feed")

    camera_snapshot = st.camera_input("Take a photo of your pose", label_visibility="collapsed")

    if camera_snapshot is None:
        st.markdown(
            """
            <div class="video-placeholder">
                🎥 Take a photo to get real feedback<br/>
                <span style="font-size:0.8rem;">
                Streamlit only allows snapshot capture in the browser (no continuous
                video stream), so click the camera button above, hold your pose, and
                each photo will be analyzed by the real model.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        analyze_clicked = st.button(
            "🔎 Analyze This Pose",
            use_container_width=True,
            type="primary",
            disabled=not BACKEND_AVAILABLE,
        )

        if analyze_clicked and BACKEND_AVAILABLE:
            with st.spinner("Detecting landmarks and scoring your pose..."):
                pil_image = Image.open(io.BytesIO(camera_snapshot.getvalue())).convert("RGB")
                rgb_frame = np.array(pil_image)
                bgr_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)

                detector = get_pose_detector()
                metrics_engine = get_metrics_engine()

                landmarks = detector.detect(bgr_frame)

                if landmarks is None:
                    st.session_state.last_message = "No person detected — step back so your full body is visible."
                    st.session_state.tips = ["Make sure your whole body is in frame", "Improve lighting if the room is dark"]
                    st.session_state.good_points = []
                    st.session_state.overlay_image = rgb_frame
                else:
                    raw_pose_data = metrics_engine.analyze(
                        landmark_data=landmarks,
                        target_pose=pose_info["backend_key"],
                    )

                    st.session_state.accuracy = raw_pose_data["score"]
                    st.session_state.last_message = raw_pose_data["message"]
                    st.session_state.tips = [
                        f.replace("_", " ") for f in raw_pose_data["feedback_list"]
                    ]
                    st.session_state.good_points = (
                        ["Perfect form on this pose!"] if raw_pose_data["is_correct"] else []
                    )
                    st.session_state.history.append(raw_pose_data["score"])

                    if raw_pose_data["is_correct"]:
                        st.session_state.reps += 1
                        st.session_state.current_streak += 1
                        st.session_state.best_streak = max(
                            st.session_state.best_streak, st.session_state.current_streak
                        )
                    else:
                        st.session_state.current_streak = 0

                    if show_skeleton:
                        overlay_bgr = detector.draw_landmarks(bgr_frame.copy())
                        st.session_state.overlay_image = cv2.cvtColor(overlay_bgr, cv2.COLOR_BGR2RGB)
                    else:
                        st.session_state.overlay_image = rgb_frame

                speak_text = st.session_state.last_message
                if st.session_state.tips:
                    speak_text += ". " + ". ".join(st.session_state.tips)
                speak_in_browser(speak_text)

        if st.session_state.overlay_image is not None:
            st.image(
                st.session_state.overlay_image,
                use_container_width=True,
                caption="Latest analyzed frame" + (" (skeleton overlay on)" if show_skeleton else ""),
            )
        else:
            st.image(camera_snapshot, use_container_width=True, caption="Captured frame — click Analyze")

        if not BACKEND_AVAILABLE:
            st.warning(
                "Real backend isn't available on this host right now, so scoring can't run. "
                "See the sidebar for the import error."
            )

with col_feedback:
    st.markdown("#### 📊 Live Feedback")

    accuracy = st.session_state.accuracy

    gauge_color = "#4CAF7D" if accuracy >= 80 else "#E8A94C" if accuracy >= 60 else "#E85A5A"
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=accuracy,
            number={"suffix": "%", "font": {"size": 36, "color": "#2F4F3E"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#2F4F3E"},
                "bar": {"color": gauge_color},
                "bgcolor": "#F0EEE7",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 60], "color": "#FBE7E5"},
                    {"range": [60, 80], "color": "#FCF3E3"},
                    {"range": [80, 100], "color": "#E6F5EA"},
                ],
            },
        )
    )
    fig.update_layout(height=220, margin=dict(l=20, r=20, t=20, b=10), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    if st.session_state.last_message:
        st.caption(st.session_state.last_message)

    if st.session_state.tips or st.session_state.good_points:
        for point in st.session_state.good_points:
            st.markdown(f'<div class="good-item">✅ {point}</div>', unsafe_allow_html=True)
        for tip in st.session_state.tips:
            st.markdown(f'<div class="tip-item">💡 {tip}</div>', unsafe_allow_html=True)
    else:
        st.info("Take a photo and click **'Analyze This Pose'** to get real feedback.")

# ----------------------------------------------------------------------------
# SESSION STATS
# ----------------------------------------------------------------------------
st.markdown("#### 📈 Session Stats")
stat1, stat2, stat3, stat4 = st.columns(4)

elapsed = 0
if st.session_state.session_active and st.session_state.start_time:
    elapsed = int(time.time() - st.session_state.start_time)

with stat1:
    st.metric("⏱️ Time Held", f"{elapsed // 60:02d}:{elapsed % 60:02d}")
with stat2:
    st.metric("✅ Correct Reps", st.session_state.reps)
with stat3:
    st.metric("🔥 Best Streak", st.session_state.best_streak)
with stat4:
    avg_acc = int(sum(st.session_state.history) / len(st.session_state.history)) if st.session_state.history else 0
    st.metric("📊 Avg Accuracy", f"{avg_acc}%")

# ----------------------------------------------------------------------------
# FOOTER NOTE
# ----------------------------------------------------------------------------
st.markdown("---")
if BACKEND_AVAILABLE:
    st.caption(
        "Built with Streamlit + MediaPipe. Each captured photo is run through the real "
        "PhysioVision pose-detection and joint-angle scoring engine."
    )
else:
    st.caption(
        "Built with Streamlit. Real backend failed to load on this host — check the "
        "sidebar for details."
    )