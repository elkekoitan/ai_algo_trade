# 📖 MARKET NARRATOR - Implementation Tasks

## Overview
Implementing an AI-powered system to generate data-driven market narratives, explaining not just *what* happened, but *why* it happened and *what* could happen next.

## Phase 1: Backend Foundation (Week 1-2)

### Task 1.1: Create Module Structure
- [ ] Create `backend/modules/market_narrator/` directory.
- [ ] Create `__init__.py`, `models.py`, `data_aggregator.py`, `sentiment_analyzer.py`, `correlation_engine.py`, and `story_generator.py`.

### Task 1.2: Implement Data Models
- [ ] In `models.py`, define Pydantic models: `MarketStory`, `MarketEvent`, `CausalityLink`, `InfluenceNode`, `MarketScenario`.
- [ ] Add enums for `EventType` (Economic, Geopolitical, Technical), `Sentiment` (Positive, Neutral, Negative), `AssetClass` (FX, Commodity, Equity, Crypto).

### Task 1.3: Data Aggregator Service
- [ ] In `data_aggregator.py`, create a service to fetch data from multiple sources.
- [ ] Implement a mock connector for economic data (e.g., CPI, NFP from a JSON file).
- [ ] Implement a mock connector for news headlines.
- [ ] Integrate with `MT5Service` to get key price levels and changes.

### Task 1.4: Sentiment Analyzer
- [ ] In `sentiment_analyzer.py`, create a basic sentiment analysis function.
- [ ] Use a simple keyword-based approach for analyzing mock news headlines (e.g., "rate hike" = negative for stocks).

## Phase 2: AI & Correlation Engine (Week 3-4)

### Task 2.1: Correlation Engine
- [ ] In `correlation_engine.py`, implement logic to find relationships in data.
- [ ] Fetch historical data for a few key assets (e.g., EURUSD, XAUUSD, DXY) from `MT5Service`.
- [ ] Calculate rolling correlations between these assets.
- [ ] Identify significant positive or negative correlations.

### Task 2.2: Story Generator (AI Core)
- [ ] In `story_generator.py`, implement the main narrative construction logic.
- [ ] Integrate with `OpenAI` client (if key is present) for advanced narrative generation.
- [ ] Create a template-based fallback system if the AI client is not available.
- [ ] Develop a function to take events, sentiment, and correlations and weave them into a `MarketStory`.
- [ ] Implement logic to create a "what-if" `MarketScenario`.

## Phase 3: API & Frontend (Week 5-6)

### Task 3.1: Create API Endpoints
- [ ] Create `backend/api/v1/market_narrator.py`.
- [ ] Implement `GET /narrator/feed` to get the main story feed.
- [ ] Implement `GET /narrator/story/{story_id}` for detailed story data, including influence maps.
- [ ] Implement a background task to periodically generate new stories.
- [ ] Integrate the new router into `main.py`.

### Task 3.2: Create Frontend Components
- [ ] Create `frontend/components/market-narrator/` directory.
- [ ] Build `StoryFeed.tsx`: A component to display a scrolling feed of `MarketStory` cards.
- [ ] Build `InfluenceMap.tsx`: A component for visualizing asset relationships (will start with a 2D version).
- [ ] Build `PersonalizedBriefing.tsx`: A component summarizing the most important story for the user.

### Task 3.3: Create Main Page
- [ ] Create `frontend/app/market-narrator/page.tsx`.
- [ ] Assemble the frontend components into a dashboard.
- [ ] Fetch data from the `/narrator/feed` endpoint and render the stories.

## Phase 4: Integration & Finalization (Week 7)

### Task 4.1: End-to-End Integration
- [ ] Ensure data flows correctly from the aggregator to the story generator and out through the API.
- [ ] Test the frontend's ability to fetch and display stories and influence maps.

### Task 4.2: Add Navigation
- [ ] Add a link to `/market-narrator` in `QuantumHeader.tsx`.

### Task 4.3: Documentation & Diagrams
- [ ] Create `adaptive-trade-manager-architecture.md` and `adaptive-trade-manager-flow.md` in `docs/diagrams/`.
- [ ] Run the script to render the diagrams to SVG/PNG.
- [ ] Update the project memory with information about the new diagrams.

### Task 4.4: Git Push
- [ ] Add all new files to Git.
- [ ] Commit the changes with a comprehensive message.
- [ ] Push the new feature to the remote repository.

## Technical Requirements
-   **Dependencies**: `openai` (optional), `scipy` (for stats, already included).
-   **Environment Variables**: `OPENAI_API_KEY` (optional).

## Success Metrics
-   **User Engagement**: High daily active users and time spent on the page.
-   **Insightfulness**: Users report gaining new insights they wouldn't have found otherwise.
-   **Narrative Clarity**: Stories are easy to understand and provide clear cause-and-effect explanations. 