from .pose_matcher import PoseMatcher


class Metrics:

    def __init__(self):

        self.pose_matcher = PoseMatcher()

    def analyze(
        self,
        landmark_data,
        target_pose="tree_pose"
    ):
        """
        Main entry point for Module 2.

        Input:
            landmark_data (from Module 1)

        Output:
            raw_pose_data (for Module 3)
        """

        raw_pose_data = self.pose_matcher.evaluate(

            landmark_data,
            target_pose

        )

        return raw_pose_data
    