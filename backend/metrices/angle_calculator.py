import math

try:
    from pose_database import get_pose
except ImportError:
    from metrices.pose_database import get_pose


class PoseCalculator:

    @staticmethod
    def calculate_angle(point_a, point_b, point_c):
        """
        Calculates the angle (0-180 degrees) formed by three landmarks.
        """

        if point_a is None or point_b is None or point_c is None:
            return None

        angle = math.degrees(

            math.atan2(
                point_c["y"] - point_b["y"],
                point_c["x"] - point_b["x"]
            )

            -

            math.atan2(
                point_a["y"] - point_b["y"],
                point_a["x"] - point_b["x"]
            )

        )

        angle = abs(angle)

        if angle > 180:
            angle = 360 - angle

        return int(round(angle))

    def compute_joint_angles(self, landmark_data):

        if landmark_data is None:
            return None

        angles = {

            "left_elbow": self.calculate_angle(

                landmark_data["left_shoulder"],
                landmark_data["left_elbow"],
                landmark_data["left_wrist"]

            ),

            "right_elbow": self.calculate_angle(

                landmark_data["right_shoulder"],
                landmark_data["right_elbow"],
                landmark_data["right_wrist"]

            ),

            "left_knee": self.calculate_angle(

                landmark_data["left_hip"],
                landmark_data["left_knee"],
                landmark_data["left_ankle"]

            ),

            "right_knee": self.calculate_angle(

                landmark_data["right_hip"],
                landmark_data["right_knee"],
                landmark_data["right_ankle"]

            ),

            "left_hip": self.calculate_angle(

                landmark_data["left_shoulder"],
                landmark_data["left_hip"],
                landmark_data["left_knee"]

            ),

            "right_hip": self.calculate_angle(

                landmark_data["right_shoulder"],
                landmark_data["right_hip"],
                landmark_data["right_knee"]

            ),

            "left_shoulder": self.calculate_angle(

                landmark_data["left_elbow"],
                landmark_data["left_shoulder"],
                landmark_data["left_hip"]

            ),

            "right_shoulder": self.calculate_angle(

                landmark_data["right_elbow"],
                landmark_data["right_shoulder"],
                landmark_data["right_hip"]

            )

        }

        return angles

    def evaluate(self, landmark_data, target_pose="tree_pose"):

        if landmark_data is None:

            return {

                "pose_name": target_pose,

                "is_correct": False,

                "score": 0,

                "message": "No landmarks detected.",

                "angles": {},

                "feedback_list": []

            }

        current_angles = self.compute_joint_angles(landmark_data)

        pose_rules = get_pose(target_pose)

        if pose_rules is None:

            return {

                "pose_name": target_pose,

                "is_correct": False,

                "score": 0,

                "message": "Unknown pose.",

                "angles": current_angles,

                "feedback_list": []

            }

        total = len(pose_rules)

        correct = 0

        feedback = []

        for joint, (minimum, maximum) in pose_rules.items():

            if joint not in current_angles:

                feedback.append(f"Missing {joint.replace('_',' ')}")

                continue

            angle = current_angles[joint]

            if minimum <= angle <= maximum:

                correct += 1

            elif angle < minimum:

                feedback.append(

                    f"Extend {joint.replace('_',' ')}"

                )

            else:

                feedback.append(

                    f"Bend {joint.replace('_',' ')}"

                )

        score = int((correct / total) * 100)

        is_correct = score >= 80

        return {

            "pose_name": target_pose,

            "is_correct": is_correct,

            "score": score,

            "message":

                "Perfect Form!"

                if is_correct

                else " | ".join(feedback),

            "angles": current_angles,

            "feedback_list": feedback

        }

