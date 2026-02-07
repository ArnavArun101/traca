import logging
import os
from typing import Optional, Dict
from app.services.llm_engine import llm_engine

logger = logging.getLogger(__name__)

class ContentGenerator:
    def __init__(self):
        pass

    async def generate_post(self, topic: str, platform: str = "linkedin") -> str:
        """
        Generate social media content using LLM.
        """
        system_prompt = (
            f"You are a professional social media manager for a trading analyst. "
            f"Generate a {platform} post about the following topic. "
            f"LinkedIn posts should be professional and insightful. "
            f"X (Twitter) posts should be concise and engaging with relevant hashtags."
        )
        
        prompt = f"Topic: {topic}\n\nDraft a post."
        
        result = await llm_engine.generate_response(prompt, system_prompt=system_prompt)
        return result.get("response", "Could not generate post draft.")

content_generator = ContentGenerator()
