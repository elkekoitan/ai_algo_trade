"""
Autonomous Trading Agents
AI agents with swarm intelligence, evolutionary algorithms, and meta-learning.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import numpy as np
import random

logger = logging.getLogger(__name__)

class AgentState(Enum):
    LEARNING = "learning"
    TRADING = "trading"
    OPTIMIZING = "optimizing"
    IDLE = "idle"
    EVOLVED = "evolved"

class AgentType(Enum):
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    ARBITRAGE = "arbitrage"
    SENTIMENT = "sentiment"
    HYBRID = "hybrid"

@dataclass
class TradingGene:
    """Genetic representation of trading strategy."""
    risk_tolerance: float
    time_horizon: int
    signal_sensitivity: float
    position_sizing: float
    stop_loss: float
    take_profit: float
    adaptability: float

@dataclass
class TradingAgent:
    """Autonomous trading agent with learning capabilities."""
    id: str
    name: str
    agent_type: AgentType
    state: AgentState
    genes: TradingGene
    performance: Dict[str, float] = field(default_factory=dict)
    learning_rate: float = 0.01
    generation: int = 0
    trades_executed: int = 0
    fitness_score: float = 0.0
    memory: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class SwarmDecision:
    """Collective decision from agent swarm."""
    action: str
    confidence: float
    participating_agents: List[str]
    consensus_level: float
    reasoning: str
    timestamp: datetime

class AutonomousTradingAgents:
    """Swarm of autonomous trading agents with evolutionary capabilities."""
    
    def __init__(self, swarm_size: int = 50):
        self.swarm_size = swarm_size
        self.agents: Dict[str, TradingAgent] = {}
        self.swarm_decisions: List[SwarmDecision] = []
        self.evolution_cycles: int = 0
        self.collective_memory: List[Dict[str, Any]] = []
        self.market_conditions: Dict[str, Any] = {}
        
    async def initialize_swarm(self):
        """Initialize the agent swarm."""
        try:
            logger.info(f"Initializing swarm of {self.swarm_size} autonomous agents")
            
            for i in range(self.swarm_size):
                agent = self._create_random_agent(f"agent_{i}")
                self.agents[agent.id] = agent
                
            logger.info(f"Swarm initialized with {len(self.agents)} agents")
            
        except Exception as e:
            logger.error(f"Error initializing swarm: {e}")
            raise
    
    def _create_random_agent(self, name_prefix: str) -> TradingAgent:
        """Create agent with random genetic traits."""
        genes = TradingGene(
            risk_tolerance=random.uniform(0.01, 0.05),
            time_horizon=random.randint(5, 120),  # 5 to 120 minutes
            signal_sensitivity=random.uniform(0.1, 0.9),
            position_sizing=random.uniform(0.1, 0.3),
            stop_loss=random.uniform(0.005, 0.02),
            take_profit=random.uniform(0.01, 0.05),
            adaptability=random.uniform(0.1, 0.9)
        )
        
        agent_types = list(AgentType)
        agent_type = random.choice(agent_types)
        
        return TradingAgent(
            id=str(uuid.uuid4()),
            name=f"{name_prefix}_{agent_type.value}",
            agent_type=agent_type,
            state=AgentState.LEARNING,
            genes=genes,
            performance={'total_return': 0.0, 'sharpe_ratio': 0.0, 'win_rate': 0.0}
        )
    
    async def swarm_intelligence_decision(self, market_data: Dict[str, Any]) -> SwarmDecision:
        """Make collective trading decision using swarm intelligence."""
        try:
            # Get individual agent decisions
            agent_votes = []
            for agent in self.agents.values():
                if agent.state in [AgentState.TRADING, AgentState.OPTIMIZING]:
                    vote = await self._get_agent_decision(agent, market_data)
                    agent_votes.append(vote)
            
            if not agent_votes:
                return SwarmDecision(
                    action="hold",
                    confidence=0.0,
                    participating_agents=[],
                    consensus_level=0.0,
                    reasoning="No active agents",
                    timestamp=datetime.now()
                )
            
            # Aggregate decisions using weighted voting
            decision = await self._aggregate_decisions(agent_votes)
            
            # Store in collective memory
            self.collective_memory.append({
                'decision': decision,
                'market_data': market_data,
                'timestamp': datetime.now()
            })
            
            # Limit memory size
            if len(self.collective_memory) > 1000:
                self.collective_memory = self.collective_memory[-1000:]
            
            self.swarm_decisions.append(decision)
            
            return decision
            
        except Exception as e:
            logger.error(f"Error in swarm intelligence decision: {e}")
            return SwarmDecision(
                action="hold",
                confidence=0.0,
                participating_agents=[],
                consensus_level=0.0,
                reasoning=f"Error: {e}",
                timestamp=datetime.now()
            )
    
    async def _get_agent_decision(self, agent: TradingAgent, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get trading decision from individual agent."""
        try:
            # Agent-specific decision logic based on type
            if agent.agent_type == AgentType.MOMENTUM:
                return await self._momentum_decision(agent, market_data)
            elif agent.agent_type == AgentType.MEAN_REVERSION:
                return await self._mean_reversion_decision(agent, market_data)
            elif agent.agent_type == AgentType.ARBITRAGE:
                return await self._arbitrage_decision(agent, market_data)
            elif agent.agent_type == AgentType.SENTIMENT:
                return await self._sentiment_decision(agent, market_data)
            else:  # HYBRID
                return await self._hybrid_decision(agent, market_data)
                
        except Exception as e:
            logger.error(f"Error getting agent decision: {e}")
            return {'action': 'hold', 'confidence': 0.0, 'agent_id': agent.id}
    
    async def _momentum_decision(self, agent: TradingAgent, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Momentum-based trading decision."""
        try:
            prices = market_data.get('prices', [])
            if len(prices) < 10:
                return {'action': 'hold', 'confidence': 0.0, 'agent_id': agent.id}
            
            # Calculate momentum
            recent_prices = prices[-10:]
            momentum = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
            
            # Apply agent's sensitivity
            signal_strength = abs(momentum) * agent.genes.signal_sensitivity
            
            if momentum > 0.001 and signal_strength > agent.genes.risk_tolerance:
                return {'action': 'buy', 'confidence': min(0.9, signal_strength * 10), 'agent_id': agent.id}
            elif momentum < -0.001 and signal_strength > agent.genes.risk_tolerance:
                return {'action': 'sell', 'confidence': min(0.9, signal_strength * 10), 'agent_id': agent.id}
            else:
                return {'action': 'hold', 'confidence': 0.5, 'agent_id': agent.id}
                
        except Exception as e:
            logger.error(f"Error in momentum decision: {e}")
            return {'action': 'hold', 'confidence': 0.0, 'agent_id': agent.id}
    
    async def _mean_reversion_decision(self, agent: TradingAgent, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mean reversion trading decision."""
        try:
            prices = market_data.get('prices', [])
            if len(prices) < 20:
                return {'action': 'hold', 'confidence': 0.0, 'agent_id': agent.id}
            
            # Calculate mean and deviation
            recent_prices = prices[-20:]
            mean_price = np.mean(recent_prices)
            current_price = recent_prices[-1]
            std_dev = np.std(recent_prices)
            
            if std_dev == 0:
                return {'action': 'hold', 'confidence': 0.0, 'agent_id': agent.id}
            
            # Z-score
            z_score = (current_price - mean_price) / std_dev
            
            # Apply agent's sensitivity
            if z_score > 2 * agent.genes.signal_sensitivity:
                return {'action': 'sell', 'confidence': min(0.9, abs(z_score) / 3), 'agent_id': agent.id}
            elif z_score < -2 * agent.genes.signal_sensitivity:
                return {'action': 'buy', 'confidence': min(0.9, abs(z_score) / 3), 'agent_id': agent.id}
            else:
                return {'action': 'hold', 'confidence': 0.5, 'agent_id': agent.id}
                
        except Exception as e:
            logger.error(f"Error in mean reversion decision: {e}")
            return {'action': 'hold', 'confidence': 0.0, 'agent_id': agent.id}
    
    async def _arbitrage_decision(self, agent: TradingAgent, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Arbitrage opportunity detection."""
        try:
            # Simplified arbitrage detection
            spread = market_data.get('spread', 0.0002)
            volume = market_data.get('volume', 0)
            
            # Look for unusual spread widening
            if spread > 0.0005 and volume > 1000:
                return {'action': 'arbitrage', 'confidence': 0.8, 'agent_id': agent.id}
            else:
                return {'action': 'hold', 'confidence': 0.3, 'agent_id': agent.id}
                
        except Exception as e:
            logger.error(f"Error in arbitrage decision: {e}")
            return {'action': 'hold', 'confidence': 0.0, 'agent_id': agent.id}
    
    async def _sentiment_decision(self, agent: TradingAgent, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sentiment-based trading decision."""
        try:
            sentiment_score = market_data.get('sentiment', 50)  # 0-100 scale
            
            # Apply agent's sensitivity to sentiment
            adjusted_sentiment = sentiment_score * agent.genes.signal_sensitivity
            
            if adjusted_sentiment > 70:
                return {'action': 'buy', 'confidence': (adjusted_sentiment - 50) / 50, 'agent_id': agent.id}
            elif adjusted_sentiment < 30:
                return {'action': 'sell', 'confidence': (50 - adjusted_sentiment) / 50, 'agent_id': agent.id}
            else:
                return {'action': 'hold', 'confidence': 0.4, 'agent_id': agent.id}
                
        except Exception as e:
            logger.error(f"Error in sentiment decision: {e}")
            return {'action': 'hold', 'confidence': 0.0, 'agent_id': agent.id}
    
    async def _hybrid_decision(self, agent: TradingAgent, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Hybrid decision combining multiple strategies."""
        try:
            # Get decisions from all strategies
            momentum_decision = await self._momentum_decision(agent, market_data)
            mean_reversion_decision = await self._mean_reversion_decision(agent, market_data)
            sentiment_decision = await self._sentiment_decision(agent, market_data)
            
            # Weight decisions based on agent's adaptability
            weights = {
                'momentum': agent.genes.adaptability,
                'mean_reversion': 1 - agent.genes.adaptability,
                'sentiment': agent.genes.signal_sensitivity
            }
            
            # Simple ensemble
            actions = [momentum_decision['action'], mean_reversion_decision['action'], sentiment_decision['action']]
            confidences = [momentum_decision['confidence'], mean_reversion_decision['confidence'], sentiment_decision['confidence']]
            
            # Majority vote with confidence weighting
            action_scores = {'buy': 0, 'sell': 0, 'hold': 0}
            for action, confidence in zip(actions, confidences):
                action_scores[action] += confidence
            
            final_action = max(action_scores.items(), key=lambda x: x[1])[0]
            final_confidence = action_scores[final_action] / sum(action_scores.values())
            
            return {'action': final_action, 'confidence': final_confidence, 'agent_id': agent.id}
            
        except Exception as e:
            logger.error(f"Error in hybrid decision: {e}")
            return {'action': 'hold', 'confidence': 0.0, 'agent_id': agent.id}
    
    async def _aggregate_decisions(self, agent_votes: List[Dict[str, Any]]) -> SwarmDecision:
        """Aggregate individual agent decisions into swarm decision."""
        try:
            if not agent_votes:
                return SwarmDecision(
                    action="hold",
                    confidence=0.0,
                    participating_agents=[],
                    consensus_level=0.0,
                    reasoning="No votes",
                    timestamp=datetime.now()
                )
            
            # Weight votes by agent fitness scores
            weighted_votes = {'buy': 0, 'sell': 0, 'hold': 0}
            total_weight = 0
            participating_agents = []
            
            for vote in agent_votes:
                agent_id = vote['agent_id']
                agent = self.agents[agent_id]
                
                # Use fitness score as weight (default to 1.0 if no fitness yet)
                weight = max(0.1, agent.fitness_score) if agent.fitness_score > 0 else 1.0
                action = vote['action']
                confidence = vote['confidence']
                
                weighted_votes[action] += weight * confidence
                total_weight += weight
                participating_agents.append(agent_id)
            
            # Normalize votes
            if total_weight > 0:
                for action in weighted_votes:
                    weighted_votes[action] /= total_weight
            
            # Find consensus
            final_action = max(weighted_votes.items(), key=lambda x: x[1])[0]
            final_confidence = weighted_votes[final_action]
            
            # Calculate consensus level (how much agents agree)
            action_counts = {'buy': 0, 'sell': 0, 'hold': 0}
            for vote in agent_votes:
                action_counts[vote['action']] += 1
            
            max_count = max(action_counts.values())
            consensus_level = max_count / len(agent_votes)
            
            reasoning = f"Swarm consensus: {len(agent_votes)} agents, {consensus_level:.1%} agreement"
            
            return SwarmDecision(
                action=final_action,
                confidence=final_confidence,
                participating_agents=participating_agents,
                consensus_level=consensus_level,
                reasoning=reasoning,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error aggregating decisions: {e}")
            return SwarmDecision(
                action="hold",
                confidence=0.0,
                participating_agents=[],
                consensus_level=0.0,
                reasoning=f"Aggregation error: {e}",
                timestamp=datetime.now()
            )
    
    async def evolve_agents(self, performance_data: Dict[str, Any]):
        """Evolve agent population based on performance."""
        try:
            # Update fitness scores
            for agent_id, performance in performance_data.items():
                if agent_id in self.agents:
                    agent = self.agents[agent_id]
                    # Fitness based on risk-adjusted returns
                    sharpe_ratio = performance.get('sharpe_ratio', 0)
                    win_rate = performance.get('win_rate', 0)
                    agent.fitness_score = (sharpe_ratio * 0.7) + (win_rate * 0.3)
            
            # Sort agents by fitness
            sorted_agents = sorted(self.agents.values(), key=lambda a: a.fitness_score, reverse=True)
            
            # Keep top performers (elitism)
            elite_count = max(5, int(self.swarm_size * 0.1))
            elite_agents = sorted_agents[:elite_count]
            
            # Remove bottom performers
            bottom_count = int(self.swarm_size * 0.2)
            agents_to_remove = sorted_agents[-bottom_count:]
            
            for agent in agents_to_remove:
                del self.agents[agent.id]
            
            # Create new agents through crossover and mutation
            while len(self.agents) < self.swarm_size:
                # Select parents from elite
                parent1 = random.choice(elite_agents)
                parent2 = random.choice(elite_agents)
                
                # Create offspring
                offspring = await self._crossover_agents(parent1, parent2)
                offspring = await self._mutate_agent(offspring)
                
                self.agents[offspring.id] = offspring
            
            self.evolution_cycles += 1
            logger.info(f"Evolution cycle {self.evolution_cycles} completed. "
                       f"Best fitness: {elite_agents[0].fitness_score:.3f}")
            
        except Exception as e:
            logger.error(f"Error evolving agents: {e}")
    
    async def _crossover_agents(self, parent1: TradingAgent, parent2: TradingAgent) -> TradingAgent:
        """Create offspring through genetic crossover."""
        try:
            # Crossover genes
            offspring_genes = TradingGene(
                risk_tolerance=(parent1.genes.risk_tolerance + parent2.genes.risk_tolerance) / 2,
                time_horizon=random.choice([parent1.genes.time_horizon, parent2.genes.time_horizon]),
                signal_sensitivity=(parent1.genes.signal_sensitivity + parent2.genes.signal_sensitivity) / 2,
                position_sizing=random.choice([parent1.genes.position_sizing, parent2.genes.position_sizing]),
                stop_loss=(parent1.genes.stop_loss + parent2.genes.stop_loss) / 2,
                take_profit=(parent1.genes.take_profit + parent2.genes.take_profit) / 2,
                adaptability=random.choice([parent1.genes.adaptability, parent2.genes.adaptability])
            )
            
            # Choose agent type from parents
            agent_type = random.choice([parent1.agent_type, parent2.agent_type])
            
            offspring = TradingAgent(
                id=str(uuid.uuid4()),
                name=f"offspring_{self.evolution_cycles}_{agent_type.value}",
                agent_type=agent_type,
                state=AgentState.LEARNING,
                genes=offspring_genes,
                generation=max(parent1.generation, parent2.generation) + 1
            )
            
            return offspring
            
        except Exception as e:
            logger.error(f"Error in crossover: {e}")
            return self._create_random_agent("crossover_error")
    
    async def _mutate_agent(self, agent: TradingAgent, mutation_rate: float = 0.1) -> TradingAgent:
        """Apply mutations to agent genes."""
        try:
            if random.random() < mutation_rate:
                # Random mutation
                mutation_factor = random.uniform(0.9, 1.1)
                
                agent.genes.risk_tolerance *= mutation_factor
                agent.genes.signal_sensitivity *= mutation_factor
                agent.genes.position_sizing *= mutation_factor
                agent.genes.adaptability *= mutation_factor
                
                # Ensure values stay within bounds
                agent.genes.risk_tolerance = max(0.001, min(0.1, agent.genes.risk_tolerance))
                agent.genes.signal_sensitivity = max(0.1, min(1.0, agent.genes.signal_sensitivity))
                agent.genes.position_sizing = max(0.01, min(0.5, agent.genes.position_sizing))
                agent.genes.adaptability = max(0.1, min(1.0, agent.genes.adaptability))
            
            return agent
            
        except Exception as e:
            logger.error(f"Error in mutation: {e}")
            return agent
    
    def get_swarm_metrics(self) -> Dict[str, Any]:
        """Get comprehensive swarm performance metrics."""
        try:
            if not self.agents:
                return {}
            
            fitness_scores = [agent.fitness_score for agent in self.agents.values()]
            
            return {
                'total_agents': len(self.agents),
                'evolution_cycles': self.evolution_cycles,
                'avg_fitness': np.mean(fitness_scores) if fitness_scores else 0,
                'max_fitness': max(fitness_scores) if fitness_scores else 0,
                'min_fitness': min(fitness_scores) if fitness_scores else 0,
                'swarm_decisions_made': len(self.swarm_decisions),
                'agent_distribution': {
                    agent_type.value: len([a for a in self.agents.values() if a.agent_type == agent_type])
                    for agent_type in AgentType
                },
                'average_generation': np.mean([agent.generation for agent in self.agents.values()]),
                'collective_memory_size': len(self.collective_memory),
                'last_decision': self.swarm_decisions[-1] if self.swarm_decisions else None
            }
            
        except Exception as e:
            logger.error(f"Error getting swarm metrics: {e}")
            return {}

class AutonomousTradingAgent:
    """
    Represents a single autonomous trading agent.
    """
    def __init__(self, agent_id: int):
        self.agent_id = agent_id

class AgentSwarm:
    def __init__(self, swarm_size: int = 50):
        self.swarm_size = swarm_size
        self.agents = []
        self.evolution_cycles = 0
        self.swarm_decisions_made = 0
        self.avg_fitness = 0.0 