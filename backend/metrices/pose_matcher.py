from .pose_database import get_pose
from .angle_calculator import PoseCalculator


class PoseMatcher:

    def __init__(self):

        self.angle_calculator = PoseCalculator()

    def evaluate(self, landmark_data, target_pose="tree_pose"):

        # No landmarks received
        if landmark_data is None:

            raw_pose_data = {

                "pose_name": target_pose,

                "is_correct": False,

                "score": 0,

                "message": "No landmarks detected.",

                "angles": {},

                "feedback_list": []

            }

            return raw_pose_data

        # Calculate all joint angles
        current_angles = self.angle_calculator.compute_joint_angles(
            landmark_data
        )

        # Get target pose
        pose_rules = get_pose(target_pose)

        if pose_rules is None:

            raw_pose_data = {

                "pose_name": target_pose,

                "is_correct": False,

                "score": 0,

                "message": f"Unknown pose '{target_pose}'.",

                "angles": current_angles,

                "feedback_list": []

            }

            return raw_pose_data

        total_joints = len(pose_rules)

        correct_joints = 0

        feedback = []

        # Compare current angles with database
        for joint_name, (minimum, maximum) in pose_rules.items():

            if joint_name not in current_angles:

                feedback.append(

                    f"Missing {joint_name.replace('_', ' ')}"

                )

                continue

            angle = current_angles[joint_name]

            if minimum <= angle <= maximum:

                correct_joints += 1

            elif angle < minimum:

                feedback.append(

                    f"Extend {joint_name.replace('_', ' ')}"

                )

            else:

                feedback.append(

                    f"Bend {joint_name.replace('_', ' ')}"

                )

        # Calculate overall score
        score = int(

            (correct_joints / total_joints) * 100

        ) if total_joints > 0 else 0

        # 80% accuracy threshold
        is_correct = score >= 80

        # Final payload for Module 3
        raw_pose_data = {

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

        return raw_pose_data
