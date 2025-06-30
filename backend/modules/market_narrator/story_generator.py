"""
AI Story Generator for the Market Narrator

The AI core that weaves data into compelling market narratives.
"""
import os
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import uuid

from backend.core.logger import setup_logger
from .models import MarketEvent, MarketStory, Sentiment, CausalityLink, DataPoint, CorrelatedEvent, MarketNarrative, DataSource, SentimentType, MarketEventType
from openai import AsyncOpenAI

logger = setup_logger(__name__)

# Placeholder for a real NLP library
class MockNLP:
    def get_sentiment(self, text: str) -> float:
        return (len(text) % 200 - 100) / 100.0
    
    def extract_keywords(self, text: str) -> List[str]:
        return [word for word in text.split() if len(word) > 5][:5]

    def summarize(self, text: str, length: int = 50) -> str:
        return " ".join(text.split()[:length]) + "..."

# Initialize a mock NLP service
mock_nlp = MockNLP()

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

class DataAggregator:
    """Aggregates data from various sources and enriches it."""

    async def fetch_data(self, sources: List[DataSource]) -> List[DataPoint]:
        """Fetch data from specified sources and convert to DataPoint models."""
        data_points = []
        for source in sources:
            # In a real implementation, this would call different APIs
            if source == DataSource.NEWS_API:
                data_points.extend(await self._fetch_mock_news())
            elif source == DataSource.TWITTER:
                data_points.extend(await self._fetch_mock_tweets())
        
        logger.info(f"Aggregated {len(data_points)} data points from {len(sources)} sources.")
        return data_points

    async def _fetch_mock_news(self) -> List[DataPoint]:
        """Fetches mock news data."""
        return [
            DataPoint(
                id=str(uuid.uuid4()),
                source=DataSource.NEWS_API,
                timestamp=datetime.now() - timedelta(hours=2),
                content="Federal Reserve hints at potential rate cuts in the next quarter, citing slowing inflation. Market reacts positively, with S&P 500 futures climbing.",
                author="Major News Outlet",
                url="https://example.com/news/1",
                sentiment_score=0.7,
                sentiment_label=SentimentType.POSITIVE,
                related_symbols=["US30", "SPX500"],
                keywords=["Federal Reserve", "rate cuts", "inflation"],
                is_verified=True,
                credibility_score=0.9
            )
        ]

    async def _fetch_mock_tweets(self) -> List[DataPoint]:
        """Fetches mock Twitter data."""
        return [
            DataPoint(
                id=str(uuid.uuid4()),
                source=DataSource.TWITTER,
                timestamp=datetime.now() - timedelta(minutes=30),
                content="BREAKING: Big tech giant announces record-breaking earnings, stock expected to soar at market open! #investing #stocks",
                author="@FinanceGuru",
                url="https://twitter.com/example/123",
                sentiment_score=0.85,
                sentiment_label=SentimentType.VERY_POSITIVE,
                related_symbols=["AAPL", "GOOGL"],
                keywords=["earnings", "tech giant", "soar"],
                is_verified=False,
                credibility_score=0.7
            )
        ]

class CorrelationEngine:
    """Analyzes data points to find correlations and significant market events."""

    async def find_events(self, data_points: List[DataPoint]) -> List[CorrelatedEvent]:
        """Identifies correlated events from a list of data points."""
        if not data_points:
            return []

        # Simple correlation logic: Group data points with overlapping symbols and close timestamps
        sorted_points = sorted(data_points, key=lambda dp: dp.timestamp)
        
        event = CorrelatedEvent(
            event_id=str(uuid.uuid4()),
            start_time=sorted_points[0].timestamp,
            end_time=sorted_points[-1].timestamp,
            event_type=MarketEventType.MARKET_SHOCK, # Generic event type
            title="Potential Market-Moving News Cluster",
            description="A cluster of related news and social media posts suggests a significant event.",
            involved_symbols=list(set(sym for dp in sorted_points for sym in dp.related_symbols)),
            correlation_strength=0.75, # Mock value
            causality_score=0.6, # Mock value
            leading_indicator=sorted_points[0].id,
            data_points=sorted_points,
            predicted_impact="High volatility expected.",
            impact_confidence=0.8
        )
        
        logger.info(f"Identified 1 correlated event involving {len(event.involved_symbols)} symbols.")
        return [event]

class StoryGenerator:
    """Generates compelling market narratives from correlated events."""

    async def create_narrative(self, event: CorrelatedEvent) -> MarketNarrative:
        """Generates a MarketNarrative from a CorrelatedEvent."""
        
        title = f"Market Buzz: {event.title}"
        summary = self._generate_summary(event)
        full_story = self._generate_full_story(event)
        
        narrative = MarketNarrative(
            narrative_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            title=title,
            summary=summary,
            full_story=full_story,
            protagonist_symbols=event.involved_symbols,
            key_theme=event.event_type.name.replace('_', ' ').title(),
            sentiment_arc=[dp.sentiment_score for dp in event.data_points],
            market_implication=f"This sequence of events suggests a {event.predicted_impact.lower()} for {', '.join(event.involved_symbols)}.",
            potential_trades=[
                {
                    "symbol": event.involved_symbols[0],
                    "action": "BUY" if sum(dp.sentiment_score for dp in event.data_points) > 0 else "SELL",
                    "reason": "Following the dominant sentiment of the narrative.",
                    "confidence": event.impact_confidence
                }
            ],
            confidence_level=event.impact_confidence,
            projected_lifespan_hours=12, # Mock value
            source_events=[event]
        )
        
        logger.info(f"Generated narrative '{title}' for symbols {narrative.protagonist_symbols}.")
        return narrative

    def _generate_summary(self, event: CorrelatedEvent) -> str:
        """Generates a short summary using the mock NLP service."""
        combined_content = " ".join([dp.content for dp in event.data_points])
        return mock_nlp.summarize(combined_content, length=30)

    def _generate_full_story(self, event: CorrelatedEvent) -> str:
        """Generates a detailed story from the event."""
        story_parts = [f"A significant market narrative is unfolding around {', '.join(event.involved_symbols)}, driven by a {event.event_type.name.lower().replace('_', ' ')}."]
        story_parts.append(f"The story began at {event.start_time.strftime('%Y-%m-%d %H:%M')} and has developed over several hours.")
        
        for dp in event.data_points:
            story_parts.append(f"At {dp.timestamp.strftime('%H:%M')}, a {dp.source.name.lower()} report from '{dp.author}' stated: \"{dp.content}\". This carried a {dp.sentiment_label.name.lower()} sentiment.")
            
        story_parts.append(f"\nThe overall sentiment arc shows a trend towards {'optimism' if sum(dp.sentiment_score for dp in event.data_points) > 0 else 'pessimism'}.")
        story_parts.append(f"With a confidence of {event.impact_confidence*100:.0f}%, the predicted impact is: {event.predicted_impact}.")
        
        return "\n\n".join(story_parts) 