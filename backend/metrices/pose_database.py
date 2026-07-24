# pose_database.py

POSE_DATABASE = {
    # --- Standing Poses ---
    "tadasana": {
        "left_elbow": (160, 180),
        "right_elbow": (160, 180),
        "left_knee": (165, 180),
        "right_knee": (165, 180),
        "left_hip": (165, 180),
        "right_hip": (165, 180),
    },
    "tree_pose": {
        "left_elbow": (150, 180),
        "right_elbow": (150, 180),
        "left_knee": (30, 60),
        "right_knee": (160, 180),
    },
    "warrior_1": {
        "left_elbow": (160, 180),
        "right_elbow": (160, 180),
        "left_knee": (85, 105),
        "right_knee": (160, 180),
        "left_hip": (120, 150),
    },
    "warrior_2": {
        "left_elbow": (160, 180),
        "right_elbow": (160, 180),
        "left_knee": (85, 105),
        "right_knee": (160, 180),
    },
    "trikonasana": {
        "left_elbow": (160, 180),
        "right_elbow": (160, 180),
        "left_knee": (160, 180),
        "right_knee": (160, 180),
        "left_hip": (80, 120),
    },
    "goddess_pose": {
        "left_elbow": (80, 105),
        "right_elbow": (80, 105),
        "left_knee": (85, 110),
        "right_knee": (85, 110),
    },
    "chair_pose": {
        "left_elbow": (160, 180),
        "right_elbow": (160, 180),
        "left_knee": (80, 110),
        "right_knee": (80, 110),
        "left_hip": (80, 110),
        "right_hip": (80, 110),
    },
    "t_pose": {
        "left_elbow": (165, 180),
        "right_elbow": (165, 180),
        "left_shoulder": (80, 100),
        "right_shoulder": (80, 100),
        "left_knee": (165, 180),
        "right_knee": (165, 180),
    },

    # --- Floor & Core Poses ---
    "plank": {
        "left_elbow": (165, 180),
        "right_elbow": (165, 180),
        "left_hip": (160, 180),
        "right_hip": (160, 180),
        "left_knee": (165, 180),
        "right_knee": (165, 180),
    },
    "cobra_pose": {
        "left_elbow": (130, 170),
        "right_elbow": (130, 170),
        "left_hip": (130, 165),
        "right_hip": (130, 165),
    },
    "downward_dog": {
        "left_elbow": (160, 180),
        "right_elbow": (160, 180),
        "left_hip": (60, 95),
        "right_hip": (60, 95),
        "left_knee": (165, 180),
        "right_knee": (165, 180),
    },

    # --- Physical Therapy & Fitness ---
    "squat_hold": {
        "left_knee": (40, 75),
        "right_knee": (40, 75),
        "left_hip": (45, 80),
        "right_hip": (45, 80),
    },
    "bicep_curl_top": {
        "left_elbow": (30, 55),
        "right_elbow": (30, 55),
    },
    "bicep_curl_bottom": {
        "left_elbow": (160, 180),
        "right_elbow": (160, 180),
    },
}


def get_pose(pose_name):
    """Retrieves the angle bounds dictionary for a given pose name."""
    return POSE_DATABASE.get(pose_name)


def get_all_poses():
    """Returns a list of all available pose names in the database."""
    return list(POSE_DATABASE.keys())