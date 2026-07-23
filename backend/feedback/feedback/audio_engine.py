import time
import threading
import pyttsx3

# Module 3: Voice Feedback Engine
class AudioFeedbackEngine:
    def __init__(self, cooldown_seconds: float = 3.0):
        self.cooldown = cooldown_seconds
        self.last_spoken_time = 0.0
        self.last_cue = ""

    def _speak_in_thread(self, message: str) -> None:
        """Runs TTS in a separate thread to prevent webcam freezing."""
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.say(message)
            engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")

    def speak_cue(self, message: str) -> None:
        """Converts text cues to non-blocking audio with cooldown throttling."""
        if not message:
            return

        current_time = time.time()
        if (current_time - self.last_spoken_time) > self.cooldown or message != self.last_cue:
            self.last_spoken_time = current_time
            self.last_cue = message
            
            # Run in thread so the video stream never freezes
            thread = threading.Thread(target=self._speak_in_thread, args=(message,), daemon=True)
            thread.start()
            
