# PhysioVision 

**Real-Time Yoga Pose Accuracy Detector**

PhysioVision is a computer-vision powered system that detects a user's body pose via webcam, compares it against ideal joint-angle ranges for a chosen yoga pose, and gives real-time accuracy scoring and corrective feedback — like a virtual yoga instructor.

Built as a Summer Training / Data Science major project.

---

## Features

- Real-time webcam pose detection using Google's MediaPipe Pose Landmarker
- Skeleton overlay with joint tracking (33 body landmarks)
- Accuracy scoring (0–100%) against 11 supported yoga/fitness poses
- Live corrective feedback per joint (e.g. "Bend left knee", "Extend right elbow")
- Interactive Streamlit web interface with pose selection, live video, and a joint-angle table
- Session recording and landmark logging support (backend)

---

## Supported Poses

`tree_pose` · `warrior_1` · `warrior_2` · `goddess_pose` · `chair_pose` · `t_pose` · `plank` · `cobra_pose` · `downward_dog` · `squat_hold` · `bicep_curl_top` · `bicep_curl_bottom`

---

## Project Architecture

The project is split into four modules:

| Module | Description | Location |
|--------|-------------|----------|
| **1. Pose Detection** | Captures webcam frames, detects body landmarks using MediaPipe | `backend/vision/` |
| **2. Accuracy Engine** | Computes joint angles and compares them against target pose rules to generate a score and feedback | `backend/metrices/` |
| **3. Data Pipeline** | Structures the `raw_pose_data` (score, feedback, angles) for consumption by the frontend | `backend/metrices/metrices.py` |
| **4. Frontend** | Streamlit web app that displays the live video, score, and feedback | `Physio-ui/` |

### How data flows

```
Webcam frame
   → Camera / PoseDetector (Module 1)   → landmark_data
   → Metrics.analyze() (Module 2 & 3)   → raw_pose_data { score, is_correct, message, angles, feedback_list }
   → App2.py (Module 4 - Streamlit)     → live video + score + feedback rendered in browser
```

---

## Project Structure

```
PhysioVision--Summer-training-major-project/
│
├── backend/
│   ├── vision/          # Pose detection (MediaPipe wrapper), camera capture
│   ├── metrices/         # Angle calculation, pose matching, scoring logic, pose database
│   ├── models/            # ML model files (pose_landmarker.task)
│   ├── recording/        # Session video/landmark recording
│   ├── utils/             # Helpers: landmark names, smoothing, orientation detection, logging
│   ├── feedback/          # Feedback generation
│   ├── logs/               # Saved landmark logs
│   ├── app.py               # Standalone desktop entry point (OpenCV window)
│   └── requirements.txt
│
├── Physio-ui/
│   ├── App2.py            # Streamlit frontend (main entry point)
│   └── requirements.txt
│
└── README.md
```

---

## Tech Stack

- **Computer Vision:** OpenCV, MediaPipe
- **Backend Logic:** Python
- **Frontend:** Streamlit, Plotly
- **Core Libraries:** NumPy, Pillow, Matplotlib

---

## Setup & Installation

### Prerequisites
- Python 3.10+ installed
- A working webcam

### 1. Clone the repository

```bash
git clone https://github.com/disha645/PhysioVision--Summer-training-major-project.git
cd PhysioVision--Summer-training-major-project
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
cd backend
pip install -r requirements.txt
cd ../Physio-ui
pip install -r requirements.txt
```

### 4. Run the app

From inside the `Physio-ui/` folder:

```bash
streamlit run App2.py
```

This opens the app in your browser at `http://localhost:8501`.

---

## Usage

1. Select a target pose from the sidebar dropdown
2. Click **Start**
3. Stand in front of your webcam so your full body is visible
4. Hold the pose — your accuracy score, correctness status, and joint-level feedback update live
5. Click **Stop** to end the session

---

## How Scoring Works

For each target pose, `pose_database.py` defines an acceptable angle range (min, max) for relevant joints. For every frame:

1. Joint angles are computed from detected landmarks (`angle_calculator.py`)
2. Each joint's angle is checked against the target pose's ideal range
3. **Score = (correct joints / total joints) × 100**
4. A pose is marked **correct** at a score threshold of **80%**
5. Any joint outside range generates specific feedback (`"Extend <joint>"` or `"Bend <joint>"`)

---

## Notes

- Standalone desktop mode (with OpenCV window, `q` to quit, `r` to record) is available by running `backend/app.py` directly.
- The Streamlit frontend (`Physio-ui/App2.py`) reuses the same backend modules (`PoseDetector`, `Metrics`) directly via Python imports — no separate REST API layer is required.

---

## Contributors

Summer Training Major Project — Data Science
