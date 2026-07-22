import os   #import libraries
import json
import cv2
from tkinter import Tk, filedialog      #for replay file picker

# Same skeleton connections used in pose_detector.py
CONNECTIONS = [

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


def choose_json():      #To choose which recording to play

    root = Tk()
    root.withdraw()     #Hide tkinter background and only show file picker window

    return filedialog.askopenfilename(

        title="Select Recording",

        filetypes=[("JSON Files","*.json")]     #Only show json files

    )


def replay(json_path):

    # Matching video path
    video_path = json_path.replace(".json", ".mp4")     #from .json to .mp4

    if not os.path.exists(video_path):

        print("Matching MP4 not found.")    #if NOT exists
        return

    # Load landmark data
    with open(json_path,"r") as file:   #open json file in read mode

        frames = json.load(file)    #convert it back into python list

    # Open recorded video
    cap = cv2.VideoCapture(video_path)  #open video
    fps = cap.get(cv2.CAP_PROP_FPS)     #for original video FPS

    if fps <= 0:
        fps = 30    #If not captured, take this

    delay = int(1000 / fps)     #Delayed to show at the original speed (computer FPS is much faster so a 20s video can be shortened to 2s because CPU reads frames faster)

    frame_index = 0     #start from first frame

    while cap.isOpened():   #keep replaying until finished

        success, frame = cap.read()

        if not success:
            break

        if frame_index >= len(frames):  #no more landmark data, then stop (Or it would crash with index out of range error)
            break

        frame_data = frames[frame_index]

        h, w, _ = frame.shape

        pixel_points = {}

        # Convert normalized coordinates to pixels
        for landmark in frame_data.values():

            x = int(landmark["x"] * w)
            y = int(landmark["y"] * h)

            pixel_points[landmark["id"]] = (x,y)

        # Draw skeleton
        for start,end in CONNECTIONS:

            if start not in pixel_points:
                continue

            if end not in pixel_points:
                continue

            cv2.line(
                frame,
                pixel_points[start],
                pixel_points[end],
                (0,255,0),
                3,
                cv2.LINE_AA
            )

        # Draw joints
        for point in pixel_points.values():

            cv2.circle(
                frame,
                point,
                5,
                (255,255,255),
                -1,
                cv2.LINE_AA
            )

        cv2.putText(
            frame,
            "Replay",
            (20,40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255,0,0),
            2
        )

        cv2.imshow(
            "Pose Replay",
            frame
        )

        frame_index += 1    #Next frame

        key = cv2.waitKey(delay) & 0xFF

        if key == ord("q"):
            break

    cap.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    json_file = choose_json()
    if json_file:
        replay(json_file)