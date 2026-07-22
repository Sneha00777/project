import json     #importing libraries AGAINNN
import os
from datetime import datetime
import cv2


class Recorder:     #for both video and landmark json

    def __init__(self):

        self.recording = False
        self.frames = []        #temporary ram list storage to append landmark dict

        self.save_folder = "recordings"
        self.video_writer = None

        os.makedirs(
            self.save_folder,       #make folder with recordings and don't crash if it already exists
            exist_ok=True
        )

        # self.filename = None

    def start(self, frame_width, frame_height, fps=30):

        self.recording = True   #recording begins
        self.frames = []        #clear prev recording

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        self.json_filename = os.path.join(      #save json file name
            self.save_folder,
            f"session_{timestamp}.json"
        )

        self.video_filename = os.path.join(     #save video file name
            self.save_folder,
            f"session_{timestamp}.mp4"
        )

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")        #fourcc - four character code, compress it in mp4 format

        self.video_writer = cv2.VideoWriter(        #video writing object with file name, compression mode and fps, etc.
            self.video_filename,
            fourcc,
            fps,
            (frame_width, frame_height)
        )

        print("Recording Started.")

    def stop(self):

        self.recording = False  #stop accepting new frames

        if self.video_writer is not None:

            self.video_writer.release()     #close mp4 file

            self.video_writer = None        #no longer active so forget it

        self.save()     #save landmark json

        print("Recording Saved.")

    def add_frame(self, frame, landmark_data):

        if not self.recording:
            return

        self.video_writer.write(frame)      #adds frames to the object video_writer

        self.frames.append(landmark_data)   #appends the data in ram temporary list "frames"

    def save(self):

        with open(self.json_filename, "w") as file:

            json.dump(
                self.frames,
                file,
                indent=4
            )