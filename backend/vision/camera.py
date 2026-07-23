#importing libraries
import cv2
from vision.pose_detector import PoseDetector #importing PoseDetector class from pose_detector.py (our own)
from utils.logger import LandmarkLogger #importing class responsible for logging landmark data
from recording.recorder import Recorder #importing class responsible for recording video and landmark data
from metrices.metrices import Metrics


class Camera:

    def __init__(self, camera_id=None): #created a dunder method to initialize the class (our camera has lot to prepare before it can start capturing frames)

        if camera_id is None:

            camera_id = self.find_available_camera() #find available camera if no camera_id is provided

        self.camera_id = camera_id #store the camera_id in the instance variable

        self.cap = cv2.VideoCapture(camera_id) #opencv function to open the webcam of the given camera_id

        if not self.cap.isOpened(): #opencv function to check if the webcam is opened successfully
            raise Exception("Could not open webcam.") #exception if FALSE

        self.detector = PoseDetector() #creating different separate objects for different tasks
        self.recorder = Recorder()
        self.logger = LandmarkLogger()
        self.metrices = Metrics()

    def find_available_camera(self, max_cameras=5): #searches for cameras available in the system and returns the first available camera id

        for camera_id in range(max_cameras):

            cap = cv2.VideoCapture(camera_id)

            if cap.isOpened():

                cap.release()

                print(f"Camera {camera_id} selected.")

                return camera_id

            cap.release()

        raise Exception("No webcam found.")

    def start(self):

        print("Camera started. Press Q to exit.")

        while True: #infinite loop to continuously capture frames from the webcam

            success, frame = self.cap.read() #if success is TRUE, frame is captured successfully as numpy array, else FALSE

            if not success:
                print("Failed to capture frame.")
                break

            frame = cv2.flip(frame, 1) #makes a mirror image to make it natural for the user

            # Detect pose
            landmarks = self.detector.detect(frame) #input frame to give landmarks as output (uses mediapipe to detect landmarks)
            if landmarks is not None:
                raw_pose_data = self.metrices.analyze(
                    landmark_data=landmarks,
                    target_pose="tree_pose"
                )

                print(raw_pose_data)
            self.logger.log(landmarks) #stores landmarks in memory (saved in ram only, not written to disk yet)

            #Records landmark data if recording is active
            self.recorder.add_frame(    #if recording, save video frame and landmark data
                frame,
                landmarks
            )

            if landmarks is not None:

                frame = self.detector.draw_landmarks(frame) #draws joints and bones on the frame using landmarks
                cv2.putText(
                    frame,
                    f"Orientation: {self.detector.get_orientation()}", #opencv function to put text on the frame (ORIENTATION OF THE USER)
                    (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 255),
                    2
                )

                status = "REC" if self.recorder.recording else "IDLE"
                color = (0, 0, 255) if self.recorder.recording else (0, 255, 0)
                cv2.putText(        #opencv function to put text on the frame (RECORDING STATUS)
                    frame,
                    status,
                    (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    color,
                    2
                )

            cv2.imshow(         #displays the image in a window
                "Real-Time Yoga Pose Tracker",
                frame
            )

            key = cv2.waitKey(1) & 0xFF     #waits 1ms for a key press

            if key == ord("r"): #ord 'r' returns ASCII value of r. if user pressed r

                if self.recorder.recording:

                    self.recorder.stop() #if recording is TRUE, stop recording

                else:

                    height, width = frame.shape[:2]     #else start recording with frame shape height and width
                    self.recorder.start(
                        width,
                        height
                    )

            elif key == ord("q"):       #if q is pressed, break the loop

                break


        self.logger.save()      #save the logging data

        if self.recorder.recording:
            self.recorder.stop()        #if recording is still active, stop it when q is pressed
            
        self.release()

    def release(self):

        self.cap.release()
        cv2.destroyAllWindows()     #release webcam and close all windows


if __name__ == "__main__":      #run the code if this file is executed directly (Otherwise importing would automatically open the webcam)

    camera = Camera()
    camera.start()