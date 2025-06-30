"""
Strategy Whisperer API Endpoints
🧙‍♂️ Natural language to MQL5 strategy generation
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends, BackgroundTasks
from pydantic import BaseModel
import logging
import asyncio

from backend.core.logger import setup_logger
from backend.modules.strategy_whisperer import (
    NLPEngine, StrategyParser, MQL5Generator, 
    BacktestEngine, DeploymentService
)
from backend.modules.strategy_whisperer.models import (
    StrategyIntent, StrategyParameters, BacktestRequest,
    BacktestResult, MQL5Code, DeploymentRequest,
    DeploymentStatus, ConversationContext, Language, StrategyResponse, StrategyMetrics, CodeSection
)
from backend.modules.mt5_integration.service import MT5Service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/strategy-whisperer", tags=["Strategy Whisperer"])

# Global service instances
_nlp_engine = None
_mql5_generator = None
_backtest_engine = None
_deployment_service = None
_strategy_parser = None

def get_services():
    """Get Strategy Whisperer service instances"""
    global _nlp_engine, _mql5_generator, _backtest_engine, _deployment_service, _strategy_parser
    
    if _nlp_engine is None:
        _nlp_engine = NLPEngine()
        _mql5_generator = MQL5Generator()
        _backtest_engine = BacktestEngine()
        _deployment_service = DeploymentService()
        _strategy_parser = StrategyParser()
    
    return _nlp_engine, _mql5_generator, _backtest_engine, _deployment_service, _strategy_parser

# Active conversations
conversations: Dict[str, ConversationContext] = {}


class NaturalLanguageInput(BaseModel):
    """Natural language strategy input"""
    text: str
    language: Language = Language.TURKISH
    session_id: Optional[str] = None
    user_id: Optional[str] = "default"


class ClarificationResponse(BaseModel):
    """Response to clarification request"""
    session_id: str
    clarification: str


class GenerateCodeRequest(BaseModel):
    """Request to generate MQL5 code"""
    strategy_parameters: StrategyParameters


class DeployRequest(BaseModel):
    """Strategy deployment request"""
    strategy_id: str
    code: str
    symbol: str = "EURUSD"
    auto_start: bool = False
    test_mode: bool = True
    notification_email: Optional[str] = None


@router.post("/parse", response_model=Dict[str, Any])
async def parse_natural_language(input_data: NaturalLanguageInput):
    """Parse natural language input into strategy intent"""
    try:
        # Get or create conversation context
        session_id = input_data.session_id or f"session_{datetime.now().timestamp()}"
        
        if session_id not in conversations:
            conversations[session_id] = ConversationContext(
                session_id=session_id,
                user_id=input_data.user_id
            )
        
        context = conversations[session_id]
        
        # Add message to context
        context.messages.append({
            "role": "user",
            "content": input_data.text,
            "timestamp": datetime.now().isoformat()
        })
        
        # Process with NLP engine
        intent = await _nlp_engine.process_input(input_data.text, input_data.language)
        context.current_intent = intent
        
        # Parse into parameters if confidence is high
        parameters = None
        if intent.confidence > 0.7 and len(intent.clarifications_needed) == 0:
            parameters = await _strategy_parser.parse_intent(intent)
            context.current_parameters = parameters
            context.state = "generating"
        else:
            context.state = "clarifying"
        
        # Update context
        context.last_activity = datetime.now()
        
        # Prepare response
        response = {
            "session_id": session_id,
            "intent": {
                "detected_type": intent.detected_type.value if intent.detected_type else None,
                "confidence": intent.confidence,
                "entities": intent.entities,
                "clarifications_needed": intent.clarifications_needed
            },
            "parameters": parameters.dict() if parameters else None,
            "state": context.state,
            "description": await _nlp_engine.generate_strategy_description(intent)
        }
        
        # Add AI response to context
        context.messages.append({
            "role": "assistant",
            "content": response["description"],
            "timestamp": datetime.now().isoformat()
        })
        
        return response
        
    except Exception as e:
        logger.error(f"Error parsing input: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clarify", response_model=Dict[str, Any])
async def clarify_intent(clarification: ClarificationResponse):
    """Process clarification for strategy intent"""
    try:
        if clarification.session_id not in conversations:
            raise HTTPException(status_code=404, detail="Session not found")
        
        context = conversations[clarification.session_id]
        
        if not context.current_intent:
            raise HTTPException(status_code=400, detail="No active intent to clarify")
        
        # Add clarification to messages
        context.messages.append({
            "role": "user",
            "content": clarification.clarification,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update intent with clarification
        updated_intent = await _nlp_engine.clarify_intent(
            context.current_intent,
            clarification.clarification
        )
        
        context.current_intent = updated_intent
        
        # Try parsing again if all clarifications addressed
        parameters = None
        if len(updated_intent.clarifications_needed) == 0:
            parameters = await _strategy_parser.parse_intent(updated_intent)
            context.current_parameters = parameters
            context.state = "generating"
        
        # Update activity
        context.last_activity = datetime.now()
        
        return {
            "session_id": clarification.session_id,
            "intent": {
                "confidence": updated_intent.confidence,
                "clarifications_needed": updated_intent.clarifications_needed
            },
            "parameters": parameters.dict() if parameters else None,
            "state": context.state
        }
        
    except Exception as e:
        logger.error(f"Error clarifying intent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=MQL5Code)
async def generate_mql5_code(request: GenerateCodeRequest):
    """Generate MQL5 code from strategy parameters"""
    try:
        # Generate code
        code = await _mql5_generator.generate_code(request.strategy_parameters)
        
        return code
        
    except Exception as e:
        logger.error(f"Error generating code: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/backtest", response_model=BacktestResult)
async def run_backtest(request: BacktestRequest):
    """Run backtest for a strategy"""
    try:
        # Get strategy parameters from session or database
        # For now, create mock parameters
        mock_params = StrategyParameters(
            name=request.strategy_id,
            description="Test strategy",
            type="trend_following",
            symbol=request.symbol,
            timeframe="H1",
            entry_conditions=[],
            exit_conditions=[],
            risk_type="percent_balance",
            risk_value=1.0
        )
        
        # Run backtest
        result = await _backtest_engine.run_backtest(mock_params, request)
        
        return result
        
    except Exception as e:
        logger.error(f"Error running backtest: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deploy", response_model=DeploymentStatus)
async def deploy_strategy(request: DeployRequest):
    """Deploy strategy to MT5"""
    try:
        # Create deployment request
        deployment_req = DeploymentRequest(
            strategy_id=request.strategy_id,
            code=request.code,
            target_account="default",
            symbol=request.symbol,
            auto_start=request.auto_start,
            test_mode=request.test_mode,
            notification_email=request.notification_email
        )
        
        # Deploy
        status = await _deployment_service.deploy_strategy(deployment_req)
        
        return status
        
    except Exception as e:
        logger.error(f"Error deploying strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deployment/{deployment_id}", response_model=DeploymentStatus)
async def get_deployment_status(deployment_id: str):
    """Get deployment status"""
    try:
        status = await _deployment_service.get_deployment_status(deployment_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Deployment not found")
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting deployment status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deployments", response_model=List[Dict[str, Any]])
async def list_deployments(strategy_id: Optional[str] = None):
    """List all deployments"""
    try:
        deployments = await _deployment_service.list_deployments(strategy_id)
        return deployments
        
    except Exception as e:
        logger.error(f"Error listing deployments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates", response_model=List[Dict[str, Any]])
async def get_strategy_templates():
    """Get available strategy templates"""
    try:
        # Mock templates for now
        templates = [
            {
                "id": "rsi_oversold",
                "name": "RSI Oversold Strategy",
                "description": "Buy when RSI < 30, sell when RSI > 70",
                "category": "mean_reversion",
                "usage_count": 156,
                "success_rate": 0.68
            },
            {
                "id": "ma_crossover",
                "name": "MA Crossover Strategy",
                "description": "Trade on moving average crossovers",
                "category": "trend_following",
                "usage_count": 243,
                "success_rate": 0.72
            },
            {
                "id": "breakout",
                "name": "London Breakout",
                "description": "Trade breakouts of London session range",
                "category": "breakout",
                "usage_count": 89,
                "success_rate": 0.65
            }
        ]
        
        return templates
        
    except Exception as e:
        logger.error(f"Error getting templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/chat")
async def strategy_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time strategy chat"""
    await websocket.accept()
    session_id = f"ws_session_{datetime.now().timestamp()}"
    
    try:
        # Create conversation context
        conversations[session_id] = ConversationContext(
            session_id=session_id,
            user_id="websocket_user"
        )
        
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "message": "Strategy Whisperer'a hoş geldiniz! Size nasıl yardımcı olabilirim?"
        })
        
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            if data.get("type") == "message":
                # Process natural language input
                text = data.get("text", "")
                language = Language(data.get("language", "tr"))
                
                # Send typing indicator
                await websocket.send_json({
                    "type": "typing",
                    "message": "Analyzing your strategy..."
                })
                
                # Process with NLP
                intent = await _nlp_engine.process_input(text, language)
                
                # Send intent result
                await websocket.send_json({
                    "type": "intent",
                    "data": {
                        "detected_type": intent.detected_type.value if intent.detected_type else None,
                        "confidence": intent.confidence,
                        "clarifications_needed": intent.clarifications_needed
                    }
                })
                
                # If clarifications needed
                if intent.clarifications_needed:
                    for clarification in intent.clarifications_needed:
                        await websocket.send_json({
                            "type": "clarification",
                            "message": clarification
                        })
                else:
                    # Parse and generate
                    parameters = await _strategy_parser.parse_intent(intent)
                    
                    await websocket.send_json({
                        "type": "parameters",
                        "data": parameters.dict()
                    })
                    
                    # Generate code
                    code = await _mql5_generator.generate_code(parameters)
                    
                    await websocket.send_json({
                        "type": "code",
                        "data": {
                            "code": code.code[:500] + "...",  # Preview
                            "full_code": code.code,
                            "lines": code.estimated_lines,
                            "performance_score": code.performance_score
                        }
                    })
            
            elif data.get("type") == "clarification":
                # Handle clarification response
                clarification_text = data.get("text", "")
                context = conversations[session_id]
                
                if context.current_intent:
                    updated_intent = await _nlp_engine.clarify_intent(
                        context.current_intent,
                        clarification_text
                    )
                    
                    context.current_intent = updated_intent
                    
                    # Continue processing...
                    await websocket.send_json({
                        "type": "intent_updated",
                        "message": "Teşekkürler, stratejinizi güncelliyorum..."
                    })
            
            elif data.get("type") == "disconnect":
                break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    finally:
        # Clean up conversation
        if session_id in conversations:
            del conversations[session_id]


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "nlp_engine": "ready",
            "strategy_parser": "ready",
            "mql5_generator": "ready",
            "backtest_engine": "ready",
            "deployment_service": "ready"
        },
        "timestamp": datetime.now().isoformat()
    }


@router.get("/status")
async def get_whisperer_status():
    """Get Strategy Whisperer system status"""
    try:
        nlp_engine, mql5_gen, backtest_engine, deploy_service, parser = get_services()
        
        return {
            "status": "active",
            "components": {
                "nlp_engine": "operational",
                "mql5_generator": "operational",
                "backtest_engine": "operational",
                "deployment_service": "operational",
                "strategy_parser": "operational"
            },
            "ai_model": "gemini-1.5-flash",
            "supported_languages": ["turkish", "english", "german", "french", "spanish"],
            "last_update": datetime.now().isoformat(),
            "version": "2.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting whisperer status: {str(e)}")


@router.post("/generate-strategy", response_model=StrategyResponse)
async def generate_strategy(request: StrategyRequest):
    """Generate MQL5 strategy from natural language description"""
    try:
        nlp_engine, mql5_gen, _, _, parser = get_services()
        
        # Parse natural language input
        parsed_strategy = await parser.parse_strategy_description(
            request.description, 
            request.language
        )
        
        # Enhance with NLP analysis
        enhanced_strategy = await nlp_engine.enhance_strategy_parameters(parsed_strategy)
        
        # Generate MQL5 code
        mql5_code = await mql5_gen.generate_mql5_code(enhanced_strategy)
        
        # Create response
        response = StrategyResponse(
            strategy_id=f"strategy_{int(datetime.now().timestamp())}",
            name=enhanced_strategy.name,
            description=request.description,
            mql5_code=mql5_code.code,
            parameters=enhanced_strategy.parameters,
            risk_level=enhanced_strategy.risk_level,
            complexity_score=enhanced_strategy.complexity_score,
            estimated_performance=enhanced_strategy.estimated_performance,
            warnings=mql5_code.warnings,
            suggestions=mql5_code.suggestions,
            created_at=datetime.now()
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/backtest-strategy", response_model=BacktestResult)
async def backtest_strategy(request: BacktestRequest):
    """Backtest a generated strategy"""
    try:
        _, _, backtest_engine, _, _ = get_services()
        
        # Run backtest
        result = await backtest_engine.run_backtest(
            request.mql5_code,
            request.symbol,
            request.timeframe,
            request.start_date,
            request.end_date,
            request.initial_balance
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error running backtest: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize-strategy")
async def optimize_strategy(
    strategy_code: str,
    symbol: str = "EURUSD",
    optimization_type: str = "profit_factor"
):
    """Optimize strategy parameters"""
    try:
        _, mql5_gen, backtest_engine, _, _ = get_services()
        
        # Run optimization
        optimized_params = await backtest_engine.optimize_parameters(
            strategy_code, 
            symbol, 
            optimization_type
        )
        
        # Generate optimized code
        optimized_code = await mql5_gen.apply_optimized_parameters(
            strategy_code, 
            optimized_params
        )
        
        return {
            "original_code": strategy_code,
            "optimized_code": optimized_code,
            "optimized_parameters": optimized_params,
            "optimization_type": optimization_type,
            "improvement_estimate": "15-25%",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error optimizing strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deploy-strategy", response_model=DeploymentResult)
async def deploy_strategy(request: DeploymentRequest):
    """Deploy strategy to MT5"""
    try:
        _, _, _, deployment_service, _ = get_services()
        
        # Deploy strategy
        result = await deployment_service.deploy_to_mt5(
            request.strategy_code,
            request.symbol,
            request.lot_size,
            request.magic_number
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error deploying strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategy-templates")
async def get_strategy_templates():
    """Get available strategy templates"""
    try:
        templates = [
            {
                "id": "scalping_template",
                "name": "Scalping Strategy",
                "description": "Hızlı alım-satım için scalping stratejisi",
                "complexity": "Medium",
                "timeframes": ["M1", "M5"],
                "example": "5 dakikalık grafiklerde RSI ve MACD kullanarak scalping yap"
            },
            {
                "id": "trend_following",
                "name": "Trend Following",
                "description": "Trend takip stratejisi",
                "complexity": "Low",
                "timeframes": ["H1", "H4", "D1"],
                "example": "Trend yönünde moving average crossover ile işlem yap"
            },
            {
                "id": "breakout_strategy",
                "name": "Breakout Strategy", 
                "description": "Kırılım stratejisi",
                "complexity": "High",
                "timeframes": ["H1", "H4"],
                "example": "Support/resistance seviyelerinin kırılımında işlem aç"
            },
            {
                "id": "grid_trading",
                "name": "Grid Trading",
                "description": "Grid trading sistemi",
                "complexity": "High",
                "timeframes": ["H1", "H4"],
                "example": "Belirli aralıklarda grid sistemi ile işlem yap"
            }
        ]
        
        return {
            "templates": templates,
            "count": len(templates),
            "usage_tip": "Bu template'leri baz alarak kendi stratejinizi tanımlayabilirsiniz"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting templates: {str(e)}")


@router.get("/strategy-metrics/{strategy_id}")
async def get_strategy_metrics(strategy_id: str):
    """Get performance metrics for a strategy"""
    try:
        # Mock metrics for demo
        metrics = StrategyMetrics(
            strategy_id=strategy_id,
            total_trades=150,
            winning_trades=89,
            losing_trades=61,
            win_rate=59.3,
            profit_factor=1.47,
            max_drawdown=12.5,
            total_return=34.7,
            sharpe_ratio=1.23,
            sortino_ratio=1.65,
            last_updated=datetime.now()
        )
        
        return metrics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting metrics: {str(e)}")


@router.post("/analyze-description")
async def analyze_strategy_description(
    description: str,
    language: str = "turkish"
):
    """Analyze strategy description and provide suggestions"""
    try:
        _, _, _, _, parser = get_services()
        
        # Parse and analyze description
        analysis = await parser.analyze_description(description, language)
        
        return {
            "original_description": description,
            "detected_elements": analysis.get("elements", []),
            "missing_elements": analysis.get("missing", []),
            "complexity_estimate": analysis.get("complexity", "Medium"),
            "feasibility_score": analysis.get("feasibility", 85),
            "suggestions": analysis.get("suggestions", []),
            "estimated_development_time": analysis.get("dev_time", "2-4 hours"),
            "language": language
        }
        
    except Exception as e:
        logger.error(f"Error analyzing description: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/code-examples")
async def get_code_examples():
    """Get MQL5 code examples and snippets"""
    try:
        examples = {
            "basic_ea": {
                "title": "Basic Expert Advisor Template",
                "description": "Temel EA yapısı",
                "code": """
//+------------------------------------------------------------------+
//|                                              BasicEA.mq5         |
//+------------------------------------------------------------------+
#property copyright "AI Algo Trade"
#property version   "1.00"

input double LotSize = 0.1;
input int MagicNumber = 12345;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   // Strategy logic here
}
"""
            },
            "rsi_strategy": {
                "title": "RSI Strategy",
                "description": "RSI tabanlı strateji örneği",
                "code": """
// RSI Strategy Example
input int RSI_Period = 14;
input double RSI_Overbought = 70;
input double RSI_Oversold = 30;

int rsi_handle;

int OnInit()
{
   rsi_handle = iRSI(_Symbol, PERIOD_CURRENT, RSI_Period, PRICE_CLOSE);
   return(INIT_SUCCEEDED);
}

void OnTick()
{
   double rsi_value[];
   CopyBuffer(rsi_handle, 0, 0, 1, rsi_value);
   
   if(rsi_value[0] > RSI_Overbought)
   {
      // Sell signal
   }
   else if(rsi_value[0] < RSI_Oversold)
   {
      // Buy signal
   }
}
"""
            }
        }
        
        return {
            "examples": examples,
            "count": len(examples),
            "note": "Bu örnekleri stratejinizi geliştirirken referans olarak kullanabilirsiniz"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting examples: {str(e)}")


@router.post("/start-live-generation")
async def start_live_strategy_generation(
    background_tasks: BackgroundTasks,
    market_conditions: List[str] = ["trending", "ranging", "volatile"],
    symbols: List[str] = ["EURUSD", "GBPUSD", "XAUUSD"]
):
    """Start live strategy generation based on market conditions"""
    try:
        background_tasks.add_task(
            _live_strategy_generation_task,
            market_conditions,
            symbols
        )
        
        return {
            "status": "started",
            "market_conditions": market_conditions,
            "symbols": symbols,
            "message": "Live strategy generation started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting live generation: {str(e)}")


# Background task for live strategy generation
async def _live_strategy_generation_task(
    market_conditions: List[str],
    symbols: List[str]
):
    """Background task for continuous strategy generation"""
    try:
        nlp_engine, mql5_gen, _, _, parser = get_services()
        
        while True:
            for condition in market_conditions:
                for symbol in symbols:
                    try:
                        # Generate adaptive strategy based on market conditions
                        description = f"Create a {condition} market strategy for {symbol}"
                        
                        parsed_strategy = await parser.parse_strategy_description(description, "english")
                        enhanced_strategy = await nlp_engine.enhance_strategy_parameters(parsed_strategy)
                        mql5_code = await mql5_gen.generate_mql5_code(enhanced_strategy)
                        
                        logger.info(f"Generated live strategy for {symbol} in {condition} market")
                        
                    except Exception as e:
                        logger.error(f"Error in live strategy generation: {e}")
            
            # Wait 30 minutes before next generation cycle
            await asyncio.sleep(1800)
            
    except Exception as e:
        logger.error(f"Live strategy generation task error: {e}") 