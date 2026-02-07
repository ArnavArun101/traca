<<<<<<< HEAD
"""Content generation service for social media posts.

Generates platform-specific content using AI personas with distinct
voices, compliance filters, and scheduling support.
"""

import logging
import json
from typing import Optional, Dict, List
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from app.services.llm_engine import llm_engine
from app.services.personas import (
    get_persona, 
    list_personas, 
    Platform, 
    AIPersona,
    CONTENT_TYPE_PROMPTS
)

logger = logging.getLogger(__name__)


class ContentStatus(Enum):
    """Content workflow status."""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    REJECTED = "rejected"


@dataclass
class GeneratedContent:
    """Represents generated social media content."""
    id: str
    persona_id: str
    platform: str
    content_type: str
    content: str
    status: ContentStatus
    created_at: datetime
    scheduled_for: Optional[datetime] = None
    published_at: Optional[datetime] = None
    market_data_snapshot: Optional[Dict] = None
    compliance_checked: bool = False
    compliance_notes: List[str] = field(default_factory=list)


# Compliance filters for financial content
COMPLIANCE_BLOCKLIST = [
    "guaranteed", "risk-free", "can't lose", "100%", "certain profit",
    "get rich", "easy money", "insider", "pump", "moon", "lambo",
    "financial advice", "you should buy", "you should sell",
    "trust me", "act now", "limited time", "secret"
]

COMPLIANCE_WARNINGS = [
    ("will", "Consider using 'may' or 'could' instead of definitive predictions"),
    ("always", "Absolute terms can be misleading in markets"),
    ("never", "Absolute terms can be misleading in markets"),
    ("profit", "Ensure profit mentions include risk context"),
]


class ContentGenerator:
    """Generates social media content with AI personas."""
    
    def __init__(self):
        self._content_cache: Dict[str, GeneratedContent] = {}
    
    def _check_compliance(self, content: str) -> tuple[bool, List[str]]:
        """
        Check content for compliance issues.
        
        Returns:
            Tuple of (is_compliant, list of issues/warnings)
        """
        issues = []
        content_lower = content.lower()
        
        # Check blocklist
        for term in COMPLIANCE_BLOCKLIST:
            if term in content_lower:
                issues.append(f"BLOCKED: Contains prohibited term '{term}'")
        
        # Check warnings
        for term, warning in COMPLIANCE_WARNINGS:
            if term in content_lower:
                issues.append(f"WARNING: {warning}")
        
        is_compliant = not any("BLOCKED" in issue for issue in issues)
        return is_compliant, issues
    
    def _format_for_platform(self, content: str, platform: Platform) -> str:
        """
        Apply platform-specific formatting.
        """
        if platform == Platform.TWITTER:
            # Split into thread if needed
            if len(content) > 280:
                return self._create_thread(content)
        return content
    
    def _create_thread(self, content: str, max_length: int = 270) -> str:
        """
        Split long content into a Twitter thread format.
        """
        sentences = content.replace('\n', ' ').split('. ')
        tweets = []
        current_tweet = ""
        tweet_num = 1
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            if not sentence.endswith('.'):
                sentence += '.'
            
            # Check if adding this sentence exceeds limit
            test_tweet = f"{current_tweet} {sentence}".strip() if current_tweet else sentence
            
            if len(test_tweet) <= max_length:
                current_tweet = test_tweet
            else:
                if current_tweet:
                    tweets.append(f"{tweet_num}/ {current_tweet}")
                    tweet_num += 1
                current_tweet = sentence
        
        # Add final tweet
        if current_tweet:
            tweets.append(f"{tweet_num}/ {current_tweet}")
        
        return "\n\n".join(tweets)

    async def generate_post(
        self, 
        topic: str, 
        platform: str = "linkedin",
        persona_id: Optional[str] = None,
        content_type: str = "market_update",
        market_data: Optional[Dict] = None,
        require_approval: bool = True
    ) -> Dict:
        """
        Generate social media content using a specific persona.
        
        Args:
            topic: The topic or market event to cover
            platform: Target platform (linkedin, twitter)
            persona_id: ID of the persona to use (defaults to marcus_reid)
            content_type: Type of content (market_update, educational, etc.)
            market_data: Optional market data to include in context
            require_approval: Whether content needs human approval
        
        Returns:
            Dict containing generated content and metadata
        """
        # Get persona
        persona = get_persona(persona_id or "marcus_reid")
        if not persona:
            return {
                "status": "error",
                "message": f"Unknown persona: {persona_id}"
            }
        
        # Get platform enum
        try:
            platform_enum = Platform(platform.lower())
        except ValueError:
            platform_enum = Platform.LINKEDIN
        
        # Build the system prompt
        system_prompt = persona.get_system_prompt(platform_enum, content_type)
        
        # Build the user prompt
        prompt_parts = [f"Topic: {topic}"]
        
        if market_data:
            prompt_parts.append(f"\nRelevant Market Data:\n{json.dumps(market_data, indent=2)}")
        
        prompt_parts.append(f"\nGenerate a {content_type.replace('_', ' ')} post for {platform}.")
        prompt = "\n".join(prompt_parts)
        
        # Generate content
        result = await llm_engine.generate_response(prompt, system_prompt=system_prompt)
        raw_content = result.get("response", "")
        
        if not raw_content or "error" in result:
            return {
                "status": "error",
                "message": result.get("error", "Failed to generate content")
            }
        
        # Format for platform
        formatted_content = self._format_for_platform(raw_content, platform_enum)
        
        # Check compliance
        is_compliant, compliance_notes = self._check_compliance(formatted_content)
        
        # Determine status
        if not is_compliant:
            status = ContentStatus.REJECTED
        elif require_approval:
            status = ContentStatus.PENDING_REVIEW
        else:
            status = ContentStatus.DRAFT
        
        # Create content object
        content_id = f"{persona.id}_{platform}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        generated = GeneratedContent(
            id=content_id,
            persona_id=persona.id,
            platform=platform,
            content_type=content_type,
            content=formatted_content,
            status=status,
            created_at=datetime.now(),
            market_data_snapshot=market_data,
            compliance_checked=True,
            compliance_notes=compliance_notes
        )
        
        # Cache it
        self._content_cache[content_id] = generated
        
        return {
            "status": "success",
            "content_id": content_id,
            "persona": {
                "id": persona.id,
                "name": persona.name,
                "title": persona.title
            },
            "platform": platform,
            "content_type": content_type,
            "content": formatted_content,
            "workflow_status": status.value,
            "compliance": {
                "passed": is_compliant,
                "notes": compliance_notes
            }
        }

    async def generate_market_update(
        self,
        symbol: str,
        price_data: Dict,
        persona_id: Optional[str] = None,
        platform: str = "linkedin"
    ) -> Dict:
        """
        Generate a market update post for a specific asset.
        """
        topic = f"{symbol} price action and market analysis"
        return await self.generate_post(
            topic=topic,
            platform=platform,
            persona_id=persona_id,
            content_type="market_update",
            market_data=price_data
        )

    async def generate_daily_summary(
        self,
        market_events: List[Dict],
        persona_id: Optional[str] = None,
        platform: str = "linkedin"
    ) -> Dict:
        """
        Generate a daily market summary.
        """
        topic = "Daily market recap and key events"
        market_data = {"events": market_events, "date": datetime.now().strftime("%Y-%m-%d")}
        
        return await self.generate_post(
            topic=topic,
            platform=platform,
            persona_id=persona_id,
            content_type="daily_summary",
            market_data=market_data
        )

    async def generate_educational_thread(
        self,
        concept: str,
        persona_id: Optional[str] = "sarah_martinez",
        platform: str = "twitter"
    ) -> Dict:
        """
        Generate an educational thread explaining a trading concept.
        """
        return await self.generate_post(
            topic=f"Explain: {concept}",
            platform=platform,
            persona_id=persona_id,
            content_type="educational"
        )

    async def generate_news_reaction(
        self,
        news_headline: str,
        news_summary: str,
        affected_assets: List[str],
        persona_id: Optional[str] = None,
        platform: str = "twitter"
    ) -> Dict:
        """
        Generate a reaction post to market news.
        """
        topic = f"News: {news_headline}"
        market_data = {
            "headline": news_headline,
            "summary": news_summary,
            "affected_assets": affected_assets
        }
        
        return await self.generate_post(
            topic=topic,
            platform=platform,
            persona_id=persona_id,
            content_type="news_reaction",
            market_data=market_data
        )

    def get_available_personas(self) -> List[Dict]:
        """Get list of available personas."""
        return list_personas()

    def get_content(self, content_id: str) -> Optional[Dict]:
        """Retrieve cached content by ID."""
        content = self._content_cache.get(content_id)
        if not content:
            return None
        return {
            "id": content.id,
            "persona_id": content.persona_id,
            "platform": content.platform,
            "content": content.content,
            "status": content.status.value,
            "created_at": content.created_at.isoformat(),
            "compliance_notes": content.compliance_notes
        }

    def approve_content(self, content_id: str) -> bool:
        """Approve content for publishing."""
        content = self._content_cache.get(content_id)
        if content and content.status == ContentStatus.PENDING_REVIEW:
            content.status = ContentStatus.APPROVED
            return True
        return False

    def reject_content(self, content_id: str, reason: str = "") -> bool:
        """Reject content."""
        content = self._content_cache.get(content_id)
        if content:
            content.status = ContentStatus.REJECTED
            if reason:
                content.compliance_notes.append(f"Rejected: {reason}")
            return True
        return False

=======
import logging
import os
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
>>>>>>> 76a861085ca3295a412df0a1c7debd59dedfbe51

content_generator = ContentGenerator()
