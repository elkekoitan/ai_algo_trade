"""
Strategy Whisperer API Endpoints
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel

from backend.core.logger import setup_logger
from backend.modules.strategy_whisperer import (
    NLPEngine, StrategyParser, MQL5Generator, 
    BacktestEngine, DeploymentService
)
from backend.modules.strategy_whisperer.models import (
    StrategyIntent, StrategyParameters, BacktestRequest,
    BacktestResult, MQL5Code, DeploymentRequest,
    DeploymentStatus, ConversationContext, Language
)
from backend.modules.mt5_integration.service import MT5Service

logger = setup_logger(__name__)

router = APIRouter(prefix="/strategy-whisperer", tags=["Strategy Whisperer"])

# Service instances
nlp_engine = NLPEngine()
strategy_parser = StrategyParser()
mql5_generator = MQL5Generator()
backtest_engine = BacktestEngine()
deployment_service = DeploymentService()

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
        intent = await nlp_engine.process_input(input_data.text, input_data.language)
        context.current_intent = intent
        
        # Parse into parameters if confidence is high
        parameters = None
        if intent.confidence > 0.7 and len(intent.clarifications_needed) == 0:
            parameters = await strategy_parser.parse_intent(intent)
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
            "description": await nlp_engine.generate_strategy_description(intent)
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
        updated_intent = await nlp_engine.clarify_intent(
            context.current_intent,
            clarification.clarification
        )
        
        context.current_intent = updated_intent
        
        # Try parsing again if all clarifications addressed
        parameters = None
        if len(updated_intent.clarifications_needed) == 0:
            parameters = await strategy_parser.parse_intent(updated_intent)
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
        code = await mql5_generator.generate_code(request.strategy_parameters)
        
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
        result = await backtest_engine.run_backtest(mock_params, request)
        
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
        status = await deployment_service.deploy_strategy(deployment_req)
        
        return status
        
    except Exception as e:
        logger.error(f"Error deploying strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deployment/{deployment_id}", response_model=DeploymentStatus)
async def get_deployment_status(deployment_id: str):
    """Get deployment status"""
    try:
        status = await deployment_service.get_deployment_status(deployment_id)
        
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
        deployments = await deployment_service.list_deployments(strategy_id)
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
                intent = await nlp_engine.process_input(text, language)
                
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
                    parameters = await strategy_parser.parse_intent(intent)
                    
                    await websocket.send_json({
                        "type": "parameters",
                        "data": parameters.dict()
                    })
                    
                    # Generate code
                    code = await mql5_generator.generate_code(parameters)
                    
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
                    updated_intent = await nlp_engine.clarify_intent(
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