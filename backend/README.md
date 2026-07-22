# PhysioVision

A real-time Physical Therapy & Yoga Pose Correction system using Computer Vision and Artificial Intelligence.

---

# Module 1 - Vision & Pose Detection

## Overview

The Vision & Pose Detection module is the foundation layer of PhysioVision.

This module handles real-time webcam processing, human pose detection, landmark extraction, stabilization, analysis preparation, and recording/replay capabilities.

The generated pose landmark data acts as the input for future modules such as:

- Yoga pose classification
- Joint angle calculation
- Posture correction
- AI feedback generation

---

# Features

## Camera & Video Processing

- Real-time webcam capture
- Webcam device management and selection
- Frame preprocessing pipeline
- Image flipping for user-facing camera view
- BGR to RGB conversion for MediaPipe processing

## AI Pose Detection

- Human pose detection using Google MediaPipe Pose Landmarker
- Real-time landmark extraction
- Professional skeleton visualization
- Landmark coordinate processing

## Landmark Processing

- Landmark smoothing to reduce tracking noise
- Visibility-based landmark filtering
- Landmark naming and indexing system
- Body center detection
- Person orientation detection

## Data Management

- Structured landmark export
- JSON landmark logging
- Session recording
- MP4 video recording
- Pose replay with skeleton overlay

---

# System Architecture

```
Webcam Input
      |
      v
Frame Preprocessing
      |
      v
MediaPipe Pose Landmarker
      |
      v
Landmark Extraction
      |
      v
Filtering & Smoothing
      |
      v
Body Analysis
      |
      v
Landmark Logging / Recording
      |
      v
Pose Analysis Module
      |
      v
Correction & Feedback System
```

---

# Project Structure

```
backend/
│
├── app.py
│
├── models/
│   └── pose_landmarker.task
│
├── vision/
│   ├── camera.py
│   └── pose_detector.py
│
├── utils/
│   ├── landmark_names.py
│   ├── landmark_smoother.py
│   ├── orientation.py
│   └── logger.py
│
├── recording/
│   ├── recorder.py
│   └── replay.py
│
├── recordings/
│
└── requirements.txt
```

---

# Module Responsibilities

This module is responsible for:

- Capturing live webcam input
- Preparing frames for AI inference
- Running MediaPipe pose detection
- Extracting human body landmarks
- Improving landmark stability
- Filtering unreliable landmarks
- Detecting body position and orientation
- Visualizing detected skeletons
- Recording user sessions
- Saving landmark data for future analysis
- Replaying recorded sessions with pose overlay

---

# Technologies Used

- Python
- OpenCV
- MediaPipe Tasks API
- NumPy

---

# Installation

### Create virtual environment

```bash
python -m venv venv
```

### Activate environment

Windows:

```bash
venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

# Running the Project

## Start Live Pose Tracking

```bash
python app.py
```

## Replay Recorded Session

```bash
python recording/replay.py
```

---

# Controls

| Key | Action |
|-----|--------|
| R | Start / Stop Recording |
| Q | Quit Application |

---

# Output

The system generates:

### Video Output

- MP4 recordings of user sessions

### Landmark Data

JSON files containing:

- Body landmark coordinates
- Landmark visibility values
- Frame information
- Tracking data

These outputs are designed to be consumed by future pose analysis and correction modules.

---

# Future Integration

The Vision & Pose Detection module provides the foundation for:

- Yoga pose recognition
- Joint angle calculation
- Posture error detection
- Real-time correction feedback
- AI-based physical therapy assistance

---

# Contributors

## Module 1 - Vision & Pose Detection

Implemented:

- Webcam pipeline
- MediaPipe integration
- Pose landmark extraction
- Frame preprocessing
- Landmark filtering and smoothing
- Body orientation detection
- Recording and replay system
- Landmark logging infrastructure
