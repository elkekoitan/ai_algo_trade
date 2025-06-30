"""
AI Story Generator for the Market Narrator

The AI core that weaves data into compelling market narratives.
"""
import os
from typing import List, Dict, Any, Optional

from backend.core.logger import setup_logger
from .models import MarketEvent, MarketStory, Sentiment, CausalityLink
from openai import AsyncOpenAI

logger = setup_logger(__name__)

class StoryGenerator:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OpenAI API key not found. Story Generator will use template-based fallbacks.")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=self.api_key)

    async def generate_story(self, events: List[MarketEvent], correlations: Dict[str, Any]) -> Optional[MarketStory]:
        """
        Takes market events and correlations and generates a single, coherent story.
        """
        if not events:
            return None

        # Identify the most important event to be the "protagonist"
        main_event = max(events, key=lambda e: self._calculate_event_importance(e))
        
        # Use AI to generate the narrative if available
        if self.client:
            try:
                return await self._generate_story_with_ai(main_event, events, correlations)
            except Exception as e:
                logger.error(f"AI story generation failed: {e}. Falling back to template.")
                return self._generate_story_with_template(main_event, events, correlations)
        else:
            return self._generate_story_with_template(main_event, events, correlations)

    def _calculate_event_importance(self, event: MarketEvent) -> int:
        """Calculates a simple importance score for an event."""
        # This can be made more sophisticated
        importance = 1
        if event.event_type == "Economic Data": importance += 3
        if event.event_type == "Central Bank": importance += 5
        if abs(event.sentiment_score) > 0.7: importance += 2
        return importance

    def _generate_story_with_template(self, main_event: MarketEvent, all_events: List[MarketEvent], correlations: Dict[str, Any]) -> MarketStory:
        """Generates a story using a simple template system."""
        logger.info(f"Generating story for '{main_event.headline}' using templates.")
        
        protagonist = main_event.symbol
        title = f"Market Focus: {protagonist} Jolted by {main_event.event_type}"
        
        # Build narrative
        narrative = f"{main_event.summary} This event appears to be the main driver in today's session for {protagonist}.\n\n"
        
        # Add secondary event effects
        causal_links = []
        for event in all_events:
            if event.event_id == main_event.event_id:
                continue
            narrative += f"Meanwhile, the {event.event_type} event, '{event.headline}', contributed to the overall market sentiment. "
            link = CausalityLink(
                source_event_id=main_event.event_id,
                target_event_id=event.event_id,
                description=f"likely influenced by",
                strength=0.6
            )
            causal_links.append(link)

        # Add correlation effects
        if protagonist in correlations:
            corr_info = correlations[protagonist][0] # Take the strongest one
            corr_asset, corr_value = corr_info
            narrative += f"\nThis move in {protagonist} has a strong {'positive' if corr_value > 0 else 'negative'} correlation of {corr_value} with {corr_asset}, which is also seeing significant movement. "

        key_takeaway = f"The primary driver for {protagonist} is the '{main_event.event_type}' event, with a notable correlation to {corr_asset}."

        return MarketStory(
            title=title,
            narrative=narrative,
            protagonist_asset=protagonist,
            key_events=all_events,
            causal_links=causal_links,
            sentiment=main_event.sentiment,
            key_takeaway=key_takeaway,
            confidence_score=0.65 # Lower confidence for templates
        )

    async def _generate_story_with_ai(self, main_event: MarketEvent, all_events: List[MarketEvent], correlations: Dict[str, Any]) -> MarketStory:
        """Generates a story using the OpenAI API for a more sophisticated narrative."""
        logger.info(f"Generating story for '{main_event.headline}' using AI.")

        prompt = self._build_ai_prompt(main_event, all_events, correlations)
        
        response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a master financial analyst and storyteller. Your task is to look at a set of market data and weave it into a compelling, insightful, and easy-to-understand narrative. Explain the cause-and-effect relationships. Output ONLY a JSON object in the specified format."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        story_json = response.choices[0].message.content
        story_data = json.loads(story_json)
        
        # We must still provide some data from our side
        story_data['key_events'] = all_events
        story_data['causal_links'] = [] # AI provides this in the narrative

        return MarketStory.parse_obj(story_data)

    def _build_ai_prompt(self, main_event: MarketEvent, all_events: List[MarketEvent], correlations: Dict[str, Any]) -> str:
        """Builds the detailed prompt for the AI."""
        
        events_str = "\n".join([f"- {e.event_type} for {e.symbol}: {e.headline} (Sentiment: {e.sentiment.value})" for e in all_events])
        correlations_str = "\n".join([f"- {asset}: {corr_info}" for asset, corr_info in correlations.items()])

        return f"""
        Here is the market data for today. The main event seems to be '{main_event.headline}'.

        **Key Events:**
        {events_str}

        **Observed Correlations:**
        {correlations_str}

        Please analyze this data and generate a market story. Identify the main protagonist asset. Explain the chain of events and the underlying reasons. What is the most important takeaway for a trader?

        **Output Format (JSON only):**
        {{
          "title": "A catchy, descriptive headline for the story.",
          "narrative": "A detailed, multi-paragraph story explaining what happened, why it happened, and what the connections are. Use a professional but engaging tone.",
          "protagonist_asset": "The main symbol the story is about (e.g., 'USDJPY').",
          "sentiment": "The overall market sentiment for the protagonist asset ('positive', 'negative', 'neutral').",
          "key_takeaway": "A single, powerful sentence summarizing the most critical insight.",
          "confidence_score": "Your confidence in this narrative, from 0.0 to 1.0."
        }}
        """

# Need to import json for the AI response parsing
import json 