import logging
from typing import Optional, Dict
from app.services.llm_engine import llm_engine

logger = logging.getLogger(__name__)


class ContentGenerator:
    def __init__(self):
        self.max_lengths = {
            "x": 280,
            "twitter": 280,
            "linkedin": 3000,
        }
        self.compliance_footer = (
            "Educational only. Not financial advice. (AI-generated)"
        )

    def _normalize_platform(self, platform: str) -> str:
        if not platform:
            return "linkedin"
        platform = platform.lower()
        if platform in ("x", "twitter"):
            return "x"
        return "linkedin"

    def _apply_length_limit(self, text: str, platform: str) -> str:
        limit = self.max_lengths.get(platform)
        if not limit:
            return text
        if len(text) <= limit:
            return text
        return text[: max(0, limit - 3)] + "..."

    async def generate_post(self, topic: str, platform: str = "linkedin") -> str:
        """
        Generate social media content using LLM.
        """
        platform = self._normalize_platform(platform)
        system_prompt = (
            f"You are a professional social media manager for a trading analyst. "
            f"Generate a {platform} post about the following topic. "
            f"LinkedIn posts should be professional and insightful. "
            f"X (Twitter) posts should be concise and engaging with relevant hashtags. "
            f"Return only the post text with no labels or headings. "
            f"Do not provide financial advice or buy/sell signals. "
            f"Include a short compliance line: '{self.compliance_footer}'."
        )

        prompt = f"Topic: {topic}\n\nDraft a post."

        result = await llm_engine.generate_response(prompt, system_prompt=system_prompt)
        response_text = result.get("response", "Could not generate post draft.")
        if platform == "x":
            lines = [line for line in response_text.splitlines() if "linkedin" not in line.lower()]
            response_text = "\n".join([line for line in lines if line.strip() != ""])
        if self.compliance_footer not in response_text:
            response_text = f"{response_text}\n\n{self.compliance_footer}"
        return self._apply_length_limit(response_text, platform)

content_generator = ContentGenerator()
