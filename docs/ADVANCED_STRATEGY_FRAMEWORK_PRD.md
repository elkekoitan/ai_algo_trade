# Advanced Strategy Framework PRD
## AI-Powered Multi-Strategy Trading System with Real-time Adaptation

### Executive Summary
Bu döküman, AI Algo Trade platformuna entegre edilecek gelişmiş strateji framework'ünün detaylı tasarımını içerir. Sistem, sınırsız sayıda strateji eklemeye izin verir, her stratejiyi AI/ML ile optimize eder ve modüller arası akıllı iletişim sağlar.

### 1. System Architecture

#### 1.1 Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     Strategy Framework Core                      │
├─────────────────────────┬───────────────────┬──────────────────┤
│   Strategy Registry     │  Event Bus Hub    │   ML Optimizer   │
├─────────────────────────┼───────────────────┼──────────────────┤
│  Performance Tracker    │ Risk Analyzer     │ Market Context   │
├─────────────────────────┼───────────────────┼──────────────────┤
│  Adaptive Parameters    │ Alert System      │  UI Framework    │
└─────────────────────────┴───────────────────┴──────────────────┘
```

#### 1.2 Event Bus Integration

```yaml
Event Categories:
  strategy.performance:
    - strategy.performance.update
    - strategy.performance.alert
    - strategy.performance.degradation
    
  strategy.optimization:
    - strategy.optimization.requested
    - strategy.optimization.completed
    - strategy.parameters.updated
    
  market.context:
    - market.volatility.changed
    - market.news.impact
    - market.sentiment.shift
    
  risk.management:
    - risk.drawdown.warning
    - risk.correlation.alert
    - risk.exposure.limit
    
  cross.module:
    - god_mode.prediction.available
    - shadow_mode.institutional.detected
    - market_narrator.story.relevant
    - adaptive_trade_manager.suggestion
```

### 2. Strategy Base Framework

#### 2.1 Abstract Base Classes

```python
# Base Strategy Interface
class IStrategy(ABC):
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize strategy with configuration"""
        pass
    
    @abstractmethod
    async def analyze(self, market_data: MarketData) -> StrategySignal:
        """Analyze market and generate signals"""
        pass
    
    @abstractmethod
    async def execute(self, signal: StrategySignal) -> ExecutionResult:
        """Execute trading signal"""
        pass
    
    @abstractmethod
    async def optimize(self, historical_data: pd.DataFrame) -> OptimizationResult:
        """Optimize strategy parameters"""
        pass
    
    @abstractmethod
    def get_parameters(self) -> StrategyParameters:
        """Get current strategy parameters"""
        pass
    
    @abstractmethod
    def set_parameters(self, params: StrategyParameters) -> None:
        """Update strategy parameters"""
        pass
```

#### 2.2 Strategy Factory Pattern

```python
class StrategyFactory:
    """Factory for creating and managing strategies"""
    
    @staticmethod
    def register_strategy(strategy_id: str, strategy_class: Type[IStrategy]):
        """Register new strategy type"""
        
    @staticmethod
    def create_strategy(strategy_id: str, config: Dict) -> IStrategy:
        """Create strategy instance"""
        
    @staticmethod
    def list_available_strategies() -> List[StrategyInfo]:
        """List all registered strategies"""
```

### 3. AI/ML Optimization Engine

#### 3.1 Strategy Optimizer Service

```python
class StrategyOptimizer:
    """AI-powered strategy parameter optimization"""
    
    async def optimize_parameters(
        self,
        strategy: IStrategy,
        historical_data: pd.DataFrame,
        optimization_goals: OptimizationGoals
    ) -> OptimizedParameters:
        """
        Optimize strategy parameters using:
        - Genetic algorithms
        - Bayesian optimization
        - Reinforcement learning
        - Walk-forward analysis
        """
        
    async def adaptive_optimization(
        self,
        strategy: IStrategy,
        real_time_performance: PerformanceMetrics
    ) -> ParameterAdjustments:
        """Real-time parameter adjustments based on performance"""
```

#### 3.2 ML Models Integration

```yaml
ML Models:
  Pattern Recognition:
    - Market regime classification
    - Volatility clustering detection
    - Trend strength analysis
    
  Performance Prediction:
    - Strategy performance forecasting
    - Drawdown prediction
    - Optimal exit timing
    
  Risk Assessment:
    - Real-time risk scoring
    - Correlation analysis
    - Black swan detection
```

### 4. Real-time Adaptation System

#### 4.1 Adaptive Parameter Service

```python
class AdaptiveParameterService:
    """Dynamic parameter adjustment based on market conditions"""
    
    async def adjust_grid_levels(
        self,
        strategy_id: str,
        market_volatility: float,
        recent_drawdowns: List[float]
    ) -> GridAdjustment:
        """
        Örnek: Altın'da volatilite arttığında grid mesafelerini genişlet
        """
        
    async def adjust_tp_sl(
        self,
        strategy_id: str,
        market_context: MarketContext,
        risk_metrics: RiskMetrics
    ) -> TPSLAdjustment:
        """
        Örnek: Haber etkisi varsa TP'yi daralt, SL'yi genişlet
        """
        
    async def adjust_lot_sizes(
        self,
        strategy_id: str,
        account_performance: AccountMetrics,
        market_conditions: MarketConditions
    ) -> LotSizeAdjustment:
        """
        Örnek: Drawdown %5'i geçerse lot size'ları küçült
        """

    async def on_market_volatility(self, data):
        if data["volatility"] > 0.8:
            await self.strategy.widen_grid_spacing(factor=1.5)
```

#### 4.2 Market Context Awareness

```python
class MarketContextService:
    """Comprehensive market context analysis"""
    
    async def analyze_market_conditions(self) -> MarketContext:
        return MarketContext(
            volatility_regime="high",  # low, medium, high, extreme
            trend_strength=0.75,       # -1 to 1
            liquidity_level="normal",  # low, normal, high
            news_impact_score=0.3,     # 0 to 1
            sentiment_score=-0.2,      # -1 to 1
            correlation_matrix={}      # Asset correlations
        )
    
    async def get_event_calendar(self) -> List[MarketEvent]:
        """Upcoming events that may impact trading"""
        
    async def social_sentiment_analysis(self) -> SentimentAnalysis:
        """Real-time social media sentiment"""
```

### 5. Cross-Module Intelligence

#### 5.1 Module Integration Examples

```python
# Example 1: Sanal-Süpürge + God Mode Integration
async def optimize_grid_with_god_mode(self):
    # God Mode'dan gelecek tahmini al
    prediction = await event_handler.request_god_mode_prediction("XAUUSD", "H1")
    if prediction and prediction["confidence"] > 0.8:
        await strategy.adjust_grid_bias(prediction["direction"])

# Example 2: Sanal-Süpürge + Shadow Mode Integration
async def detect_institutional_activity(self):
    shadow_data = await self.event_bus.request(
        "shadow_mode.get_institutional_flow",
        {"symbol": self.symbol}
    )
    
    if shadow_data.dark_pool_activity > 0.7:
        # Kurumsal hareket var, grid'i genişlet
        await self.widen_grid_spacing(factor=1.5)

# Example 3: Sanal-Süpürge + Market Narrator Integration
async def adjust_for_market_story(self):
    market_story = await self.event_bus.request(
        "market_narrator.get_current_narrative",
        {"symbol": self.symbol}
    )
    
    if "risk_off" in market_story.themes:
        # Risk-off sentiment, pozisyonları küçült
        await self.reduce_position_sizes(factor=0.5)
```

### 6. Risk Management Integration

#### 6.1 Dynamic Risk Controls

```python
class RiskAnalyzer:
    """Real-time risk analysis and management"""
    
    async def analyze_strategy_risk(
        self,
        strategy_id: str,
        open_positions: List[Position]
    ) -> RiskAnalysis:
        return RiskAnalysis(
            current_drawdown=self.calculate_drawdown(),
            var_95=self.calculate_var(0.95),
            correlation_risk=self.analyze_correlations(),
            max_loss_scenario=self.worst_case_analysis(),
            recommended_actions=self.generate_risk_actions()
        )
    
    async def emergency_risk_management(
        self,
        risk_event: RiskEvent
    ) -> EmergencyAction:
        """
        Acil durum risk yönetimi:
        - Tüm pozisyonlara SL koy
        - Lot size'ları küçült
        - Yeni giriş durdur
        """
```

#### 6.2 Optional SL/TP System

```python
class DynamicSLTPManager:
    """Intelligent SL/TP management"""
    
    async def calculate_optimal_sl(
        self,
        strategy: IStrategy,
        position: Position,
        market_context: MarketContext
    ) -> StopLoss:
        """
        Faktörler:
        - ATR-based volatility
        - Support/resistance levels
        - Account risk percentage
        - Correlation with other positions
        """
    
    async def trailing_stop_logic(
        self,
        position: Position,
        price_movement: PriceData
    ) -> TrailingStopAdjustment:
        """Akıllı trailing stop mantığı"""
```

### 7. Alert & Notification System

#### 7.1 Intelligent Alert Service

```python
class AlertSystem:
    """Multi-channel alert system"""
    
    async def create_alert(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        context: AlertContext
    ) -> Alert:
        """
        Alert Types:
        - PERFORMANCE_DEGRADATION
        - RISK_THRESHOLD_BREACH
        - MARKET_OPPORTUNITY
        - SYSTEM_ANOMALY
        - OPTIMIZATION_SUGGESTION
        """
    
    async def send_alert(
        self,
        alert: Alert,
        channels: List[NotificationChannel]
    ):
        """
        Channels:
        - In-app notification
        - Email
        - SMS
        - WhatsApp
        - Telegram
        - Discord
        """
```

### 8. Performance Tracking System

#### 8.1 Granular Performance Metrics

```python
class PerformanceTracker:
    """Detailed performance tracking per strategy"""
    
    async def track_performance(
        self,
        strategy_id: str,
        timeframe: TimeFrame
    ) -> PerformanceReport:
        return PerformanceReport(
            # Basic Metrics
            total_pnl=1234.56,
            win_rate=0.68,
            profit_factor=1.85,
            sharpe_ratio=1.92,
            
            # Advanced Metrics
            calmar_ratio=2.34,
            sortino_ratio=2.87,
            max_consecutive_wins=12,
            max_consecutive_losses=3,
            
            # Parameter Performance
            parameter_sensitivity={
                "grid_distance": 0.34,  # Impact score
                "lot_multiplier": 0.67,
                "tp_points": 0.45
            },
            
            # Market Condition Performance
            performance_by_volatility={
                "low": {"win_rate": 0.72, "avg_profit": 45.2},
                "medium": {"win_rate": 0.65, "avg_profit": 67.8},
                "high": {"win_rate": 0.58, "avg_profit": 89.3}
            }
        )
```

### 9. Frontend Integration Framework

#### 9.1 Generic Strategy Components

```typescript
// Reusable strategy UI components

interface IStrategyComponent {
  // Common strategy display interface
  strategyId: string;
  displayName: string;
  icon: React.ComponentType;
  
  // Common methods
  renderSettings(): JSX.Element;
  renderPerformance(): JSX.Element;
  renderActivePositions(): JSX.Element;
  renderRiskMetrics(): JSX.Element;
}

// Strategy Settings Component
const StrategySettings: React.FC<{strategy: IStrategy}> = ({strategy}) => {
  return (
    <GlassCard>
      <DynamicParameterForm 
        parameters={strategy.parameters}
        onChange={handleParameterChange}
      />
      <OptimizationControls 
        onOptimize={handleOptimization}
      />
      <RiskControls 
        riskSettings={strategy.riskSettings}
      />
    </GlassCard>
  );
};
```

### 10. Implementation Roadmap

#### Phase 1: Foundation (Week 1-2)
- [ ] Create base strategy interfaces and abstract classes
- [ ] Implement strategy registry and factory
- [ ] Setup event bus adapters for strategies
- [ ] Create basic performance tracking

#### Phase 2: AI/ML Integration (Week 3-4)
- [ ] Implement parameter optimization engine
- [ ] Integrate ML models for pattern recognition
- [ ] Create adaptive parameter service
- [ ] Setup backtesting framework

#### Phase 3: Real-time Systems (Week 5-6)
- [ ] Implement market context service
- [ ] Create risk analyzer with real-time monitoring
- [ ] Setup alert and notification system
- [ ] Implement emergency risk management

#### Phase 4: Cross-Module Integration (Week 7-8)
- [ ] Connect with God Mode predictions
- [ ] Integrate Shadow Mode institutional tracking
- [ ] Link Market Narrator stories
- [ ] Setup Adaptive Trade Manager suggestions

#### Phase 5: UI/UX Implementation (Week 9-10)
- [ ] Create generic strategy components
- [ ] Implement strategy configuration UI
- [ ] Build performance dashboards
- [ ] Add real-time monitoring views

### 11. Example Scenarios

#### Scenario 1: Altın Volatilite Adaptasyonu
```python
# Altın'da volatilite arttığında otomatik grid genişletme
async def handle_gold_volatility():
    volatility = await market_context.get_volatility("XAUUSD")
    
    if volatility > 0.8:  # Yüksek volatilite
        # Grid mesafelerini %50 artır
        await sanal_supurge.adjust_grid_spacing(factor=1.5)
        
        # TP'yi genişlet (daha fazla kar potansiyeli)
        await sanal_supurge.adjust_tp(multiplier=1.3)
        
        # God Mode'dan tahmin al
        prediction = await god_mode.get_prediction("XAUUSD")
        if prediction.confidence > 0.8:
            # Güvenilir tahmin varsa lot size artır
            await sanal_supurge.adjust_lot_multiplier(1.2)
```

#### Scenario 2: Haber Etkisi Yönetimi
```python
# Önemli haber öncesi risk yönetimi
async def handle_news_event(event: NewsEvent):
    if event.impact == "high":
        # Market Narrator'dan analiz al
        narrative = await market_narrator.analyze_news_impact(event)
        
        # Tüm açık pozisyonlara SL ekle
        for position in active_positions:
            optimal_sl = await risk_analyzer.calculate_news_sl(
                position, event, narrative
            )
            await position.set_stop_loss(optimal_sl)
        
        # Kullanıcıyı uyar
        await alert_system.send_alert(
            AlertType.NEWS_WARNING,
            f"Önemli haber: {event.title}. SL'ler otomatik ayarlandı.",
            channels=["app", "telegram"]
        )
```

#### Scenario 3: Performans Degradasyonu
```python
# Strateji performansı düştüğünde otomatik optimizasyon
async def handle_performance_degradation(strategy_id: str):
    recent_performance = await performance_tracker.get_recent(
        strategy_id, days=7
    )
    
    if recent_performance.win_rate < 0.4:  # Win rate %40'ın altında
        # ML optimizer'ı çalıştır
        new_params = await ml_optimizer.emergency_optimization(
            strategy_id,
            optimization_goal="maximize_win_rate"
        )
        
        # Parametreleri güncelle
        await strategy.update_parameters(new_params)
        
        # Shadow Mode'dan kurumsal aktivite kontrol et
        institutional_activity = await shadow_mode.check_activity()
        if institutional_activity.is_against_us:
            # Kurumlar tersimizde, stratejiyi duraklat
            await strategy.pause_trading()
            await alert_system.critical_alert(
                "Kurumsal hareket tespit edildi. Strateji duraklatıldı."
            )
```

### 12. Database Schema Extensions

```sql
-- Strategy Registry Table
CREATE TABLE strategy_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_id VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(20) NOT NULL,
    parameters_schema JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Strategy Instances Table  
CREATE TABLE strategy_instances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_id VARCHAR(100) REFERENCES strategy_registry(strategy_id),
    user_id UUID REFERENCES users(id),
    instance_name VARCHAR(255),
    parameters JSONB NOT NULL,
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance History Table
CREATE TABLE strategy_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instance_id UUID REFERENCES strategy_instances(id),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metrics JSONB NOT NULL, -- Detailed performance metrics
    market_conditions JSONB, -- Market state at time of recording
    parameter_snapshot JSONB -- Parameters at time of recording
);

-- Optimization History Table
CREATE TABLE optimization_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instance_id UUID REFERENCES strategy_instances(id),
    optimization_type VARCHAR(50),
    old_parameters JSONB,
    new_parameters JSONB,
    improvement_metrics JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Alert History Table
CREATE TABLE strategy_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instance_id UUID REFERENCES strategy_instances(id),
    alert_type VARCHAR(50),
    severity VARCHAR(20),
    message TEXT,
    context JSONB,
    acknowledged BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 13. API Endpoints

```yaml
Strategy Management:
  POST   /api/v1/strategies/register         # Register new strategy type
  GET    /api/v1/strategies/list            # List available strategies
  POST   /api/v1/strategies/create-instance # Create strategy instance
  GET    /api/v1/strategies/{id}/status     # Get strategy status
  POST   /api/v1/strategies/{id}/start      # Start strategy
  POST   /api/v1/strategies/{id}/stop       # Stop strategy
  PUT    /api/v1/strategies/{id}/parameters # Update parameters

Optimization:
  POST   /api/v1/optimization/run           # Run optimization
  GET    /api/v1/optimization/{id}/status   # Get optimization status
  GET    /api/v1/optimization/history       # Get optimization history
  POST   /api/v1/optimization/backtest      # Run backtest

Performance:
  GET    /api/v1/performance/{id}/metrics   # Get performance metrics
  GET    /api/v1/performance/{id}/report    # Get detailed report
  GET    /api/v1/performance/compare        # Compare strategies

Risk Management:
  GET    /api/v1/risk/{id}/analysis        # Get risk analysis
  POST   /api/v1/risk/{id}/set-limits      # Set risk limits
  GET    /api/v1/risk/alerts               # Get risk alerts

Market Context:
  GET    /api/v1/market/context            # Get market context
  GET    /api/v1/market/volatility         # Get volatility data
  GET    /api/v1/market/events             # Get upcoming events
```

### 14. Security Considerations

```yaml
Security Measures:
  Authentication:
    - JWT token validation for all endpoints
    - API key for external integrations
    
  Authorization:
    - Role-based access control (RBAC)
    - Strategy ownership validation
    
  Data Protection:
    - Encryption for sensitive parameters
    - Secure storage of API keys
    
  Rate Limiting:
    - Per-user rate limits
    - Per-strategy execution limits
    
  Audit Trail:
    - All parameter changes logged
    - Trade execution audit log
```

### 15. Performance Requirements

```yaml
Performance Targets:
  Latency:
    - Strategy signal generation: <10ms
    - Parameter optimization: <5 seconds
    - Cross-module communication: <50ms
    - UI updates: <100ms
    
  Throughput:
    - Handle 1000+ concurrent strategies
    - Process 10,000+ events/second
    - Support 100+ users simultaneously
    
  Reliability:
    - 99.9% uptime for core services
    - Graceful degradation on failures
    - Automatic recovery mechanisms
```

Bu PRD, projenizin mevcut yapısına tam uyumlu, genişletilebilir ve her türlü stratejiyi destekleyebilen bir framework sunuyor. Event bus entegrasyonu, AI/ML optimizasyonu ve modüller arası iletişim tamamen kapsanmış durumda. 

# Yeni strateji eklemek çok kolay
@register_strategy(
    strategy_id="ict_breaker_blocks",
    display_name="ICT Breaker Blocks Strategy",
    tags=["ict", "smart-money", "institutional"]
)
class ICTBreakerBlockStrategy(StrategyBase):
    # Implementation... 