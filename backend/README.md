# AI Yoga Pose Correction 🧘

A Streamlit-based web app that will use webcam input to detect and correct yoga poses in real time.

## Current Status

✅ UI/Layout complete
🔲 Pose detection model — **not yet integrated** (TODO)

This version has the full frontend built with dummy/simulated data so the interface can be tested and demoed. The actual pose-estimation model (e.g. MediaPipe Pose) still needs to be plugged in — search for `TODO: MODEL LOGIC HERE` comments inside `App2.py` to find exactly where.

## Features (UI)

- Pose selector (Tadasana, Vrikshasana, Trikonasana, Bhujangasana, Warrior II)
- Webcam feed area (currently snapshot-based via `st.camera_input`)
- Live accuracy gauge
- Real-time correction tips panel
- Session stats: time held, correct reps, best streak, average accuracy
- "Simulate Detection" button to demo feedback without a live model

## Tech Stack

- Python
- Streamlit
- Plotly (for the accuracy gauge)

## Setup

```bash
# clone the repo
git clone <repo-url>
cd <repo-folder>

# create/activate virtual environment
uv venv
.venv\Scripts\activate

# install dependencies
uv pip install -r requirements.txt

# run the app
uv run streamlit run App2.py
```

## Next Steps

- [ ] Integrate `streamlit-webrtc` for continuous real-time webcam feed (instead of snapshot mode)
- [ ] Add pose-estimation model (MediaPipe Pose / OpenPose / custom model)
- [ ] Compare detected joint angles against ideal reference angles per pose
- [ ] Replace dummy tips/accuracy with real model output

## Team

_Add collaborator names here_
