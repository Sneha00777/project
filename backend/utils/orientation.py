class OrientationDetector:

    def __init__(self):

        self.front_threshold = 0.18

    def detect(self, landmark_data):

        if landmark_data is None:
            return "unknown"

        left_shoulder = landmark_data["left_shoulder"]
        right_shoulder = landmark_data["right_shoulder"]

        shoulder_width = abs(
            left_shoulder["x"] -
            right_shoulder["x"]
        )

        # Person is facing camera
        if shoulder_width > self.front_threshold:
            return "front"

        # Side view shoulders overlap so we use its distance from the camera to detect which side
        left_z = left_shoulder["z"]
        right_z = right_shoulder["z"]

        if left_z < right_z:
            return "left_side"

        return "right_side"