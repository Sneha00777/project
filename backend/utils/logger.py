import json     #importing libraries
import os
from datetime import datetime


class LandmarkLogger:

    def __init__(self):

        self.logs_folder = "logs"

        os.makedirs(    #create a folder "logs"
            self.logs_folder,
            exist_ok=True   #if already exists, no error
        )

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")    #convert date-time into string

        self.file_path = os.path.join(
            self.logs_folder,
            f"session_{timestamp}.json"
        )

        self.frames = []    #store in ram

    def log(self, landmarks):

        if landmarks is None:
            return

        frame = {   #creating a dictionary

            "timestamp": datetime.now().isoformat(),

            "landmarks": landmarks

        }

        self.frames.append(frame)   #keep adding

    def save(self):

        with open(      #create writing mode file
            self.file_path,
            "w"
        ) as file:

            json.dump(  #converts python list into json text and writes in the file
                self.frames,
                file,
                indent=4
            )

        print(f"Session saved to {self.file_path}")