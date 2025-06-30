from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import sqlite3
import pandas as pd
from typing import List, Dict, Any

router = APIRouter()

DB_PATH = "advanced_crypto_performance.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/status", summary="Get the overall status of the auto trader")
def get_status() -> Dict[str, Any]:
    """
    Retrieves the latest performance snapshot from the database.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM performance ORDER BY timestamp DESC LIMIT 1")
        latest_status = cursor.fetchone()
        conn.close()
        
        if latest_status:
            return dict(latest_status)
        
        return {"status": "No performance data available."}
    except Exception as e:
        # Veritabanı veya tablo henüz yoksa
        if "no such table" in str(e):
             raise HTTPException(status_code=404, detail="Performance data not found. The trader might not have run yet.")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/positions", summary="Get current open positions from MT5")
def get_positions() -> List[Dict[str, Any]]:
    """
    This endpoint is a placeholder. In a real scenario, this would
    connect to the live MT5 instance to get open positions.
    For this version, it will return an empty list.
    A more advanced implementation would use a shared data service (like Redis)
    that the trader updates periodically.
    """
    # NOTE: This is a simplified implementation.
    # A real implementation would require IPC or a shared service like Redis
    # to get live data from the running MT5 trader script.
    return []

@router.get("/trade-history", summary="Get the last 50 trades")
def get_trade_history() -> List[Dict[str, Any]]:
    """
    Retrieves the last 50 closed trades from the performance database.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trades ORDER BY timestamp DESC LIMIT 50")
        trades = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return trades
    except Exception as e:
         if "no such table" in str(e):
             raise HTTPException(status_code=404, detail="Trades data not found. The trader might not have run yet.")
         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/equity-curve", summary="Get data for the equity curve chart")
def get_equity_curve() -> List[Dict[str, Any]]:
    """
    Provides data points for charting the account balance and equity over time.
    """
    try:
        conn = get_db_connection()
        # Fetch last 1000 performance points for the chart
        query = "SELECT timestamp, balance, equity FROM performance ORDER BY timestamp ASC LIMIT 1000"
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            return []
            
        # Format for charting libraries
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.rename(columns={"timestamp": "time"})
        
        return df.to_dict(orient="records")
    except Exception as e:
        if "no such table" in str(e):
             raise HTTPException(status_code=404, detail="Performance data not found. The trader might not have run yet.")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") 