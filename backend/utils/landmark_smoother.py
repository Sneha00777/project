#we need to smooth the landmark cause it jitters without manually doing it so

class LandmarkSmoother:

    def __init__(self, alpha=0.5):

        self.alpha = alpha
        self.previous_landmarks = None

    def smooth(self, landmarks):

        if landmarks is None:
            return None

        # First frame
        if self.previous_landmarks is None:

            self.previous_landmarks = landmarks #can't average with one frame so return as it is
            return landmarks

        smoothed = {}   #empty dictionary

        for name, current in landmarks.items():

            previous = self.previous_landmarks[name]

#Using exponential smoothing/ weighted average
#alpha is smoothing factor deciding how much importance should be given to current and previous frames

            smoothed[name] = {

                "id": current["id"],

                "x": self.alpha * current["x"] +
                     (1 - self.alpha) * previous["x"],

                "y": self.alpha * current["y"] +
                     (1 - self.alpha) * previous["y"],

                "z": self.alpha * current["z"] +
                     (1 - self.alpha) * previous["z"],

                "visibility": current["visibility"],

                "visible": current["visible"]

            }

        self.previous_landmarks = smoothed

        return smoothed

#alpha 0- never moves, 0.2- very smooth, more lag, 0.5- balanced, 0.8-less smooth, responsive, 1- no smoothing at all