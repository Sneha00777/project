import os
from google import genai
from google.genai import types

# Module 3: AI Assistant for ANY Pose
class PhysioAIAssistant:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY missing")
            
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = "gemini-2.5-flash"
        
        self.system_instruction = (
            "You are PhysioVision AI, a physical therapy and yoga instructor. "
            "Analyze posture feedback, joint angles, and user questions for ANY exercise or pose. "
            "Give clear, actionable advice under 3 sentences."
        )

    def analyze_pose_correction(self, raw_pose_data: dict, user_query: str = "") -> str:
        # Dynamic AI analysis for raw pose data or queries
        prompt = f"""
        System: {self.system_instruction}
        Pose Data: {raw_pose_data}
        User Query: {user_query if user_query else 'Give real-time pose guidance.'}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=150,
                    temperature=0.3
                )
            )
            return response.text.strip()
        except Exception as e:
            return f"AI Error: {e}"
