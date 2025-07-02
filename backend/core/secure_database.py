"""
Secure Database Helper Module
Provides SQL injection protected database operations
"""

import re
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import uuid
from supabase import Client
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class SecureDatabaseHelper:
    """Helper class for secure database operations"""
    
    # SQL injection patterns to block
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|EXEC|EXECUTE)\b)",
        r"(--|\*|\/\*|\*\/)",
        r"(;|\||&&)",
        r"(xp_|sp_)",
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)",
        r"(\'|\"|`)",
        r"(\bHAVING\b|\bGROUP BY\b)",
        r"(\bINTO\b|\bFROM\b)",
    ]
    
    # Allowed characters for different field types
    FIELD_PATTERNS = {
        'uuid': r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$',
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'phone': r'^\+?[0-9\s\-\(\)]+$',
        'alphanumeric': r'^[a-zA-Z0-9]+$',
        'alpha_with_space': r'^[a-zA-Z\s]+$',
        'numeric': r'^[0-9]+$',
        'decimal': r'^[0-9]+\.?[0-9]*$',
        'safe_text': r'^[a-zA-Z0-9\s\-_.,!?@#$%&*()+=]+$',
        'symbol': r'^[A-Z0-9]+$',
        'server_name': r'^[a-zA-Z0-9\-_.]+$',
        'timeframe': r'^(M1|M5|M15|M30|H1|H4|D1|W1|MN1)$',
    }
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
    
    def validate_input(self, value: Any, field_type: str, field_name: str) -> Any:
        """Validate and sanitize input based on field type"""
        if value is None:
            return None
        
        # Convert to string for validation
        str_value = str(value)
        
        # Check for SQL injection patterns
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, str_value, re.IGNORECASE):
                logger.warning(f"Potential SQL injection in {field_name}: {pattern}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid characters in {field_name}"
                )
        
        # Validate based on field type
        if field_type in self.FIELD_PATTERNS:
            pattern = self.FIELD_PATTERNS[field_type]
            if not re.match(pattern, str_value):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid format for {field_name}"
                )
        
        # Type-specific validation and conversion
        if field_type == 'uuid':
            try:
                uuid.UUID(str_value)
                return str_value
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid UUID format for {field_name}"
                )
        
        elif field_type in ['numeric', 'decimal']:
            try:
                return float(str_value) if field_type == 'decimal' else int(str_value)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid number format for {field_name}"
                )
        
        elif field_type == 'boolean':
            return str_value.lower() in ['true', '1', 'yes', 'on']
        
        elif field_type == 'datetime':
            try:
                return datetime.fromisoformat(str_value).isoformat()
            except:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid datetime format for {field_name}"
                )
        
        return str_value
    
    def safe_select(self, table: str, columns: List[str] = ["*"], 
                   filters: Optional[Dict[str, Any]] = None,
                   limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Perform safe SELECT query with validation"""
        try:
            # Validate table name
            if not re.match(r'^[a-zA-Z_]+$', table):
                raise ValueError("Invalid table name")
            
            # Build query
            query = self.client.table(table).select(*columns)
            
            # Apply filters safely
            if filters:
                for field, value in filters.items():
                    # Validate field name
                    if not re.match(r'^[a-zA-Z_]+$', field):
                        raise ValueError(f"Invalid field name: {field}")
                    
                    # Use Supabase's parameterized methods
                    if isinstance(value, dict):
                        operator = value.get('operator', 'eq')
                        val = value.get('value')
                        
                        if operator == 'eq':
                            query = query.eq(field, val)
                        elif operator == 'neq':
                            query = query.neq(field, val)
                        elif operator == 'gt':
                            query = query.gt(field, val)
                        elif operator == 'gte':
                            query = query.gte(field, val)
                        elif operator == 'lt':
                            query = query.lt(field, val)
                        elif operator == 'lte':
                            query = query.lte(field, val)
                        elif operator == 'like':
                            query = query.like(field, f"%{val}%")
                        elif operator == 'ilike':
                            query = query.ilike(field, f"%{val}%")
                        elif operator == 'in':
                            query = query.in_(field, val)
                        else:
                            raise ValueError(f"Unsupported operator: {operator}")
                    else:
                        query = query.eq(field, value)
            
            # Apply limit
            if limit:
                if not isinstance(limit, int) or limit < 1 or limit > 1000:
                    limit = 100
                query = query.limit(limit)
            
            # Execute query
            result = query.execute()
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Safe select error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database query failed"
            )
    
    def safe_insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform safe INSERT with validation"""
        try:
            # Validate table name
            if not re.match(r'^[a-zA-Z_]+$', table):
                raise ValueError("Invalid table name")
            
            # Validate all data fields
            validated_data = {}
            for field, value in data.items():
                # Validate field name
                if not re.match(r'^[a-zA-Z_]+$', field):
                    raise ValueError(f"Invalid field name: {field}")
                
                # Skip None values
                if value is not None:
                    validated_data[field] = value
            
            # Use Supabase client - no SQL injection risk
            result = self.client.table(table).insert(validated_data).execute()
            
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(f"Safe insert error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database insert failed"
            )
    
    def safe_update(self, table: str, data: Dict[str, Any], 
                   filters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform safe UPDATE with validation"""
        try:
            # Validate table name
            if not re.match(r'^[a-zA-Z_]+$', table):
                raise ValueError("Invalid table name")
            
            # Validate data fields
            validated_data = {}
            for field, value in data.items():
                if not re.match(r'^[a-zA-Z_]+$', field):
                    raise ValueError(f"Invalid field name: {field}")
                validated_data[field] = value
            
            # Build update query
            query = self.client.table(table).update(validated_data)
            
            # Apply filters safely
            for field, value in filters.items():
                if not re.match(r'^[a-zA-Z_]+$', field):
                    raise ValueError(f"Invalid filter field: {field}")
                query = query.eq(field, value)
            
            # Execute update
            result = query.execute()
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(f"Safe update error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database update failed"
            )
    
    def safe_delete(self, table: str, filters: Dict[str, Any]) -> bool:
        """Perform safe DELETE with validation"""
        try:
            # Validate table name
            if not re.match(r'^[a-zA-Z_]+$', table):
                raise ValueError("Invalid table name")
            
            # Must have at least one filter to prevent accidental full table delete
            if not filters:
                raise ValueError("Delete operation requires at least one filter")
            
            # Build delete query
            query = self.client.table(table).delete()
            
            # Apply filters safely
            for field, value in filters.items():
                if not re.match(r'^[a-zA-Z_]+$', field):
                    raise ValueError(f"Invalid filter field: {field}")
                query = query.eq(field, value)
            
            # Execute delete
            query.execute()
            return True
            
        except Exception as e:
            logger.error(f"Safe delete error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database delete failed"
            )
    
    def safe_count(self, table: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """Perform safe COUNT with validation"""
        try:
            # Validate table name
            if not re.match(r'^[a-zA-Z_]+$', table):
                raise ValueError("Invalid table name")
            
            # Build count query
            query = self.client.table(table).select("*", count="exact")
            
            # Apply filters if provided
            if filters:
                for field, value in filters.items():
                    if not re.match(r'^[a-zA-Z_]+$', field):
                        raise ValueError(f"Invalid filter field: {field}")
                    query = query.eq(field, value)
            
            # Execute count
            result = query.execute()
            return result.count if hasattr(result, 'count') else 0
            
        except Exception as e:
            logger.error(f"Safe count error: {e}")
            return 0
    
    def validate_trading_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate trading-specific parameters"""
        validated = {}
        
        # Symbol validation
        if 'symbol' in params:
            validated['symbol'] = self.validate_input(
                params['symbol'], 'symbol', 'symbol'
            )
        
        # Volume validation
        if 'volume' in params:
            volume = self.validate_input(params['volume'], 'decimal', 'volume')
            if volume <= 0 or volume > 100:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Volume must be between 0.01 and 100"
                )
            validated['volume'] = volume
        
        # Price validation
        for price_field in ['price', 'stop_loss', 'take_profit', 'open_price']:
            if price_field in params:
                price = self.validate_input(params[price_field], 'decimal', price_field)
                if price < 0:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"{price_field} must be positive"
                    )
                validated[price_field] = price
        
        # Order type validation
        if 'order_type' in params:
            order_type = params['order_type'].upper()
            if order_type not in ['BUY', 'SELL', 'BUY_LIMIT', 'SELL_LIMIT', 
                                 'BUY_STOP', 'SELL_STOP']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid order type"
                )
            validated['order_type'] = order_type
        
        # Timeframe validation
        if 'timeframe' in params:
            validated['timeframe'] = self.validate_input(
                params['timeframe'], 'timeframe', 'timeframe'
            )
        
        return validated 