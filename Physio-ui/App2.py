"""
AI Yoga Pose Correction — UI Layout Only
==========================================
Ye sirf UI/frontend hai. Actual pose detection model ka logic abhi nahi laga hai —
jahan bhi model plug karna hai wahan "TODO: MODEL LOGIC HERE" comment likha hai.
Abhi ke liye dummy/random data se panel demo hota hai (Simulate button se).

Run karne ke liye:
    pip install streamlit plotly
    streamlit run app.py
"""

import streamlit as st
import plotly.graph_objects as go
import random
import time
from datetime import datetime

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
# CUSTOM CSS — calming wellness palette (sage green / cream / warm coral accent)
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
        .stApp {
            background-color: #F7F5EF;
        }
        .main-header {
            font-size: 2.2rem;
            font-weight: 700;
            color: #2F4F3E;
            margin-bottom: 0;
        }
        .sub-header {
            font-size: 1rem;
            color: #6B7A6F;
            margin-top: 0;
        }
        .card {
            background-color: #FFFFFF;
            border-radius: 16px;
            padding: 1.3rem 1.5rem;
            box-shadow: 0 2px 10px rgba(47, 79, 62, 0.08);
            margin-bottom: 1rem;
        }
        .pose-pill {
            display: inline-block;
            background-color: #E4EEE6;
            color: #2F4F3E;
            padding: 4px 14px;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-right: 6px;
        }
        .tip-item {
            background-color: #FFF4EC;
            border-left: 4px solid #E8845A;
            padding: 8px 12px;
            border-radius: 6px;
            margin-bottom: 8px;
            font-size: 0.92rem;
            color: #4A3B33;
        }
        .good-item {
            background-color: #EAF6EE;
            border-left: 4px solid #4CAF7D;
            padding: 8px 12px;
            border-radius: 6px;
            margin-bottom: 8px;
            font-size: 0.92rem;
            color: #22412E;
        }
        .video-placeholder {
            background-color: #1F2A24;
            color: #A8C3B1;
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
            color: #2F4F3E;
        }
        .stButton>button {
            border-radius: 10px;
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# POSE DATA (dummy reference data — swap/extend as needed)
# ----------------------------------------------------------------------------
POSES = {
    "Tadasana (Mountain Pose)": {
        "emoji": "🧍",
        "difficulty": "Beginner",
        "description": "Stand tall, feet together, spine straight, shoulders relaxed.",
        "tip_pool": [
            "Chin thoda neeche karo, neck straight rakho",
            "Weight dono paon pe equally distribute karo",
            "Shoulders ko relax karo, kaano se door",
            "Core thoda engage karo, pet andar",
        ],
        "good_pool": [
            "Spine alignment perfect hai",
            "Feet position sahi hai",
            "Balance achha maintain ho raha hai",
        ],
    },
    "Vrikshasana (Tree Pose)": {
        "emoji": "🌳",
        "difficulty": "Beginner",
        "description": "One foot on inner thigh, hands raised, balance on standing leg.",
        "tip_pool": [
            "Standing knee ko thoda lock mat karo",
            "Raised foot ko thigh pe aur upar rakho",
            "Hips ko level rakho, ek side tilt mat hone do",
            "Gaze ek fixed point pe rakho for balance",
        ],
        "good_pool": [
            "Balance bahut stable hai",
            "Hip alignment sahi hai",
            "Arms position accurate hai",
        ],
    },
    "Trikonasana (Triangle Pose)": {
        "emoji": "📐",
        "difficulty": "Intermediate",
        "description": "Wide-legged stance, one hand down to shin/floor, other reaching up.",
        "tip_pool": [
            "Front knee ko lock mat karo, thoda soft rakho",
            "Chest ko ceiling ki taraf zyada khulo",
            "Back foot ko 90 degree pe rakho",
            "Reach hand ko aur stretch karo",
        ],
        "good_pool": [
            "Side bend angle correct hai",
            "Leg alignment achha hai",
            "Chest opening sahi direction mein hai",
        ],
    },
    "Bhujangasana (Cobra Pose)": {
        "emoji": "🐍",
        "difficulty": "Beginner",
        "description": "Lying on stomach, lift chest with hands, gentle backbend.",
        "tip_pool": [
            "Shoulders ko kaano se door push karo",
            "Elbows ko thoda bend rakho, fully lock mat karo",
            "Pelvis ko floor pe rakho, zyada mat uthao",
            "Neck ko neutral rakho, zyada peeche mat le jao",
        ],
        "good_pool": [
            "Backbend depth theek hai",
            "Shoulder position accurate hai",
            "Elbow angle sahi hai",
        ],
    },
    "Virabhadrasana II (Warrior II)": {
        "emoji": "⚔️",
        "difficulty": "Intermediate",
        "description": "Wide stance, front knee bent 90°, arms extended parallel to floor.",
        "tip_pool": [
            "Front knee ko aur bend karo, 90 degree tak",
            "Front knee ankle ke exactly upar rakho",
            "Arms ko shoulder height pe level rakho",
            "Torso ko side mein mat jhukao, seedha rakho",
        ],
        "good_pool": [
            "Knee angle perfect 90 degree hai",
            "Arm alignment sahi hai",
            "Torso position stable hai",
        ],
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

    sensitivity = st.slider("Detection sensitivity", 1, 10, 6)
    show_skeleton = st.checkbox("Show skeleton overlay (future)", value=True)

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
    st.caption("⚙️ Model status: **Not connected yet**. UI is running on dummy/demo data.")

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

    # TODO: MODEL LOGIC HERE
    # Yahan streamlit-webrtc (ya cv2 + st.image loop) laga ke continuous webcam
    # stream lena hai, aur har frame ko pose-estimation model (MediaPipe / OpenPose /
    # custom CNN) ko bhejna hai. Model se joints/keypoints milenge, unhe overlay
    # karke yahi placeholder replace karna hai.

    camera_snapshot = st.camera_input("Webcam preview (snapshot mode for now)", label_visibility="collapsed")

    if camera_snapshot is None:
        st.markdown(
            """
            <div class="video-placeholder">
                🎥 Webcam feed will appear here<br/>
                <span style="font-size:0.8rem;">
                (Currently using Streamlit's camera_input for layout.<br/>
                Swap with streamlit-webrtc for continuous real-time feed once model is ready.)
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.image(camera_snapshot, use_container_width=True, caption="Captured frame (pose overlay will render here)")

    st.button(
        "🔄 Simulate Detection (Demo only)",
        help="Randomly generates feedback since the real model isn't connected yet",
        use_container_width=True,
        key="simulate_btn",
    )

with col_feedback:
    st.markdown("#### 📊 Live Feedback")

    # --- Simulate button logic ---
    if st.session_state.simulate_btn:
        st.session_state.accuracy = random.randint(55, 98)
        st.session_state.tips = random.sample(pose_info["tip_pool"], k=min(2, len(pose_info["tip_pool"])))
        st.session_state.good_points = random.sample(pose_info["good_pool"], k=min(2, len(pose_info["good_pool"])))
        if st.session_state.accuracy >= 80:
            st.session_state.reps += 1
            st.session_state.current_streak += 1
            st.session_state.best_streak = max(st.session_state.best_streak, st.session_state.current_streak)
        else:
            st.session_state.current_streak = 0
        st.session_state.history.append(st.session_state.accuracy)

    accuracy = st.session_state.accuracy

    # --- Accuracy gauge ---
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

    # --- Tips / good points ---
    if st.session_state.tips or st.session_state.good_points:
        for point in st.session_state.good_points:
            st.markdown(f'<div class="good-item">✅ {point}</div>', unsafe_allow_html=True)
        for tip in st.session_state.tips:
            st.markdown(f'<div class="tip-item">💡 {tip}</div>', unsafe_allow_html=True)
    else:
        st.info("Click **'Simulate Detection'** neeche se demo feedback dekhne ke liye.")

    # TODO: MODEL LOGIC HERE
    # Real model ready hone ke baad, upar wale tips/good_points ki jagah model ke
    # actual joint-angle comparison results (ideal vs detected angle) yahan feed karna hai.

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
st.caption(
    "Built with Streamlit • This is a UI-only prototype — pose estimation model "
    "(e.g. MediaPipe Pose) is not yet wired in. Search 'TODO: MODEL LOGIC HERE' in app.py "
    "to find where to plug it in."
)
