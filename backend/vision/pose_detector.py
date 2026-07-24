import os
import cv2          #importing libraries
import mediapipe as mp      #importing google's mediapipe library (Actual AI)

from utils.landmark_names import LANDMARK_NAMES
from utils.landmark_smoother import LandmarkSmoother
from utils.orientation import OrientationDetector

# backend/vision/pose_detector.py -> parent is backend/vision, parent.parent is backend/
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MODEL_PATH = os.path.join(_BACKEND_DIR, "models", "pose_landmarker.task")


class PoseDetector:

    def __init__(self):

        self.model_path = _MODEL_PATH     #absolute path, works regardless of current working directory    #storing the model path

        #Mediapipe classes
        BaseOptions = mp.tasks.BaseOptions
        PoseLandmarker = mp.tasks.vision.PoseLandmarker
        PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = PoseLandmarkerOptions(        #configuring AI

            base_options=BaseOptions(
                model_asset_path=self.model_path        #without this, mediapipe wouldn't know which model to use
            ),

            running_mode=VisionRunningMode.IMAGE,       #choosing the mode

            num_poses=1     #only track 1 person

        )

        self.detector = PoseLandmarker.create_from_options(options)     #creates the AI using all the settings we just gave it

        self.result = None      #entire object returned by mediapipe containing pose landmarks, world landmarks, etc. We specifically want pose of person 0 from this.
        self.landmark_data = None
        self.smoother = LandmarkSmoother(alpha=0.5)
        self.orientation_detector = OrientationDetector()
        self.orientation = "unknown"
        self.body_center = None
        self.visibility_threshold = 0.5     #confidence score

        # Skeleton connections list
        self.connections = [

            # Face
            (0, 1), (1, 2), (2, 3),
            (0, 4), (4, 5), (5, 6),

            # Shoulders
            (11, 12),

            # Left Arm
            (11, 13),
            (13, 15),

            # Right Arm
            (12, 14),
            (14, 16),

            # Torso
            (11, 23),
            (12, 24),
            (23, 24),

            # Left Leg
            (23, 25),
            (25, 27),
            (27, 31),

            # Right Leg
            (24, 26),
            (26, 28),
            (28, 32),

            # Feet
            (27, 29),
            (29, 31),

            (28, 30),
            (30, 32)

        ]

    def detect(self, frame):

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  #opencv stores in BGR but mediapipe needs RGB format so we convert

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,       #Mediapipe doesn't accept numpy array or opencv format so we convert it into image format it accepts
            data=rgb
        )

        self.result = self.detector.detect(mp_image)        #gave the image to AI for landmarks detection

        if not self.result.pose_landmarks:      #If none is standing, return None
            return None

        self.landmark_data = self.get_landmark_data()

        self.landmark_data = self.smoother.smooth(  #passing the dictionary into smoother to smooth
            self.landmark_data
        )

        self.orientation = self.orientation_detector.detect(    #passing new smoothed landmark data to get orientation
            self.landmark_data
        )

        self.body_center = self.get_body_center()   #and body center

        return self.landmark_data

    def draw_landmarks(self, frame):

        if self.landmark_data is None: #None then return as it is
            return frame

        h, w, _ = frame.shape   #Get shape from numpy array (ignore channel)

        pixel_points = {}   #empty dictionary

        # Convert normalized coordinates to pixels
        for name, landmark in self.landmark_data.items():

            if not landmark["visible"]:        #Skip if the visibility is less than 0.5
                continue

            x = int(landmark["x"] * w)      #We got x and y in percentages like (if x=0.5 means 50% across the width) to calculate accurate position we multiply by width and height of the frame
            y = int(landmark["y"] * h)

            pixel_points[name] = (x, y)     #Insert the values we got into the dictionary

        # Draw skeleton
        for start, end in self.connections: #start and end in the tuple we created

            start_name = LANDMARK_NAMES[start]      #cause pixel points uses names and we can check now
            end_name = LANDMARK_NAMES[end]

            if start_name not in pixel_points:      #skip if not in pixel points
                continue

            if end_name not in pixel_points:        #Again skip
                continue

            cv2.line(
                frame,
                pixel_points[start_name],       #Draw line on the frame using opencv function from start to end point in green color and 3 thickness
                pixel_points[end_name],
                (0, 255, 0),
                3,
                cv2.LINE_AA     #Smoother edges
            )

        # Draw joints
        for point in pixel_points.values():

            cv2.circle(     #draw circle at each coordinate
                frame,
                point,
                5,
                (255, 255, 255),
                -1,
                cv2.LINE_AA
            )


            # Draw Body Center
            if self.body_center is not None:

                center_x = int(self.body_center["x"] * w)   #converting again to pixel coordinates
                center_y = int(self.body_center["y"] * h)

                cv2.circle(
                    frame,
                    (center_x, center_y),
                    7,
                    (255, 0, 0),
                    -1,
                    cv2.LINE_AA
                )

        return frame

    def get_landmark_data(self):

        if self.result is None:
            return None

        if not self.result.pose_landmarks:  #if no one is standing in front of cam
            return None

        landmarks = self.result.pose_landmarks[0]   #First person's landmarks

        landmark_data = {}

        for index, landmark in enumerate(landmarks):        #To get both numbers and names (object such as eyes, nose, etc etc.)

            landmark_name = LANDMARK_NAMES.get(
                index,                          #stores the landmark's name
                f"landmark_{index}" #won't crash if index is 99 or smth
            )

            landmark_data[landmark_name] = {        #getting details

                "id": index,

                "x": landmark.x,
                "y": landmark.y,
                "z": landmark.z,

                "visibility": landmark.visibility,
                "visible": landmark.visibility >= self.visibility_threshold     #if less than 0.5 threshold False if more then TRUE 

            }

        return landmark_data

    def get_orientation(self):

        return self.orientation #getting orientation

    def get_body_center(self):

        if self.landmark_data is None:
            return None

        if self.orientation == "front":

            left_hip = self.landmark_data["left_hip"]
            right_hip = self.landmark_data["right_hip"]

            center_x = (        #calculating center for front, left, right orientations
                left_hip["x"] +
                right_hip["x"]
            ) / 2

            center_y = (
                left_hip["y"] +
                right_hip["y"]
            ) / 2

        elif self.orientation == "left_side":

            hip = self.landmark_data["left_hip"]

            center_x = hip["x"]
            center_y = hip["y"]

        elif self.orientation == "right_side":

            hip = self.landmark_data["right_hip"]

            center_x = hip["x"]
            center_y = hip["y"]

        else:

            return None

        return {

            "x": center_x,
            "y": center_y

        }

    def get_body_center_coordinates(self):

        return self.body_center

    def get_landmark(self, landmark_index):


        if self.result is None:
            return None

        if not self.result.pose_landmarks:
            return None

        return self.result.pose_landmarks[0][landmark_index]