# PhysioVision

A real-time Physical Therapy & Yoga Pose Correction system using Computer Vision and Artificial Intelligence.

---

## Module 1 - Vision & Pose Detection

This module is responsible for capturing video from a webcam, detecting the user's body pose, processing landmarks, and providing the foundation for pose analysis.

---

## Features

- Real-time webcam capture
- AI-based pose detection using MediaPipe Pose Landmarker
- Professional skeleton rendering
- Landmark export
- Landmark smoothing
- Landmark visibility filtering
- Person orientation detection
- Body center detection
- Landmark logging
- Session recording (MP4 + JSON)
- Pose replay with skeleton overlay

---

## Project Structure

backend/
│
├── app.py
│
├── models/
│ └── pose_landmarker.task
│
├── vision/
│ ├── camera.py
│ └── pose_detector.py
│
├── utils/
│ ├── landmark_names.py
│ ├── landmark_smoother.py
│ ├── orientation.py
│ └── logger.py
│
├── recording/
│ ├── recorder.py
│ └── replay.py
│
├── recordings/
│
└── requirements.txt

---

## Technologies Used

- Python
- OpenCV
- MediaPipe Tasks API
- NumPy

---

## Installation

Create a virtual environment.

```bash
python -m venv venv
```

Activate it.

Windows:

```bash
venv\Scripts\activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

## Running the Project

Start the live pose tracker.

```bash
python app.py
```

Replay a recorded session.

```bash
python recording/replay.py
```

---

## Controls

# Key and Actions

R - Start / Stop Recording
Q - Quit Application

---

## Output

The application records:

- MP4 video
- JSON landmark data

These can later be replayed with skeleton overlay.

---

## Contributors

Module 1 – Vision & Pose Detection