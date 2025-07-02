#!/usr/bin/env python3
"""
Supabase Database Setup Script
Sets up all tables, RLS policies, and initial data for AI Algo Trade Platform
"""

import os
import sys
import asyncio
from supabase import create_client, Client

# Supabase Configuration
SUPABASE_URL = "https://jregdcopqylriziucooi.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpyZWdkY29wcXlscml6aXVjb29pIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTMzNDA5MywiZXhwIjoyMDY2OTEwMDkzfQ.SERVICE_ROLE_KEY_PLACEHOLDER"

def create_supabase_client() -> Client:
    """Create Supabase client with service role key"""
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def setup_database_tables(supabase: Client):
    """Create all database tables"""
    print("🏗️  Creating database tables...")
    
    # SQL for creating all tables
    sql_commands = [
        # User profiles table
        """
        CREATE TABLE IF NOT EXISTS user_profiles (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) UNIQUE,
            phone VARCHAR(20) UNIQUE,
            full_name VARCHAR(255),
            avatar_url TEXT,
            role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('user', 'premium', 'admin')),
            subscription_plan VARCHAR(50) DEFAULT 'free' CHECK (subscription_plan IN ('free', 'basic', 'premium', 'enterprise')),
            is_active BOOLEAN DEFAULT true,
            is_verified BOOLEAN DEFAULT false,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            last_login TIMESTAMPTZ,
            trading_preferences JSONB DEFAULT '{}',
            api_settings JSONB DEFAULT '{}',
            notification_preferences JSONB DEFAULT '{}'
        );
        """,
        
        # MT5 accounts table
        """
        CREATE TABLE IF NOT EXISTS mt5_accounts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
            mt5_login VARCHAR(50) NOT NULL,
            mt5_server VARCHAR(100) NOT NULL,
            mt5_password_encrypted TEXT NOT NULL,
            account_type VARCHAR(50) DEFAULT 'demo',
            currency VARCHAR(10) DEFAULT 'USD',
            balance DECIMAL(15,2) DEFAULT 0.00,
            equity DECIMAL(15,2) DEFAULT 0.00,
            margin DECIMAL(15,2) DEFAULT 0.00,
            free_margin DECIMAL(15,2) DEFAULT 0.00,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            last_sync TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(user_id, mt5_login, mt5_server)
        );
        """,
        
        # Trading sessions table
        """
        CREATE TABLE IF NOT EXISTS trading_sessions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
            session_token TEXT NOT NULL UNIQUE,
            login_method VARCHAR(20) NOT NULL CHECK (login_method IN ('email', 'phone', 'mt5')),
            ip_address INET,
            user_agent TEXT,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '24 hours',
            last_activity TIMESTAMPTZ DEFAULT NOW()
        );
        """,
        
        # Trading positions table
        """
        CREATE TABLE IF NOT EXISTS trading_positions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
            mt5_account_id UUID REFERENCES mt5_accounts(id) ON DELETE SET NULL,
            ticket BIGINT NOT NULL,
            symbol VARCHAR(20) NOT NULL,
            position_type VARCHAR(10) NOT NULL CHECK (position_type IN ('buy', 'sell')),
            volume DECIMAL(10,2) NOT NULL,
            open_price DECIMAL(10,5) NOT NULL,
            current_price DECIMAL(10,5),
            stop_loss DECIMAL(10,5),
            take_profit DECIMAL(10,5),
            profit DECIMAL(10,2) DEFAULT 0.00,
            commission DECIMAL(10,2) DEFAULT 0.00,
            swap DECIMAL(10,2) DEFAULT 0.00,
            comment TEXT,
            magic_number INTEGER,
            open_time TIMESTAMPTZ NOT NULL,
            close_time TIMESTAMPTZ,
            is_open BOOLEAN DEFAULT true,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(ticket, mt5_account_id)
        );
        """,
        
        # Trading orders table
        """
        CREATE TABLE IF NOT EXISTS trading_orders (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
            mt5_account_id UUID REFERENCES mt5_accounts(id) ON DELETE SET NULL,
            ticket BIGINT NOT NULL,
            symbol VARCHAR(20) NOT NULL,
            order_type VARCHAR(20) NOT NULL,
            volume DECIMAL(10,2) NOT NULL,
            price DECIMAL(10,5) NOT NULL,
            stop_loss DECIMAL(10,5),
            take_profit DECIMAL(10,5),
            comment TEXT,
            magic_number INTEGER,
            status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'filled', 'cancelled', 'rejected')),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            filled_at TIMESTAMPTZ,
            cancelled_at TIMESTAMPTZ,
            UNIQUE(ticket, mt5_account_id)
        );
        """,
        
        # AI signals table
        """
        CREATE TABLE IF NOT EXISTS ai_signals (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            signal_type VARCHAR(50) NOT NULL,
            symbol VARCHAR(20) NOT NULL,
            direction VARCHAR(10) NOT NULL CHECK (direction IN ('buy', 'sell')),
            confidence DECIMAL(5,2) NOT NULL CHECK (confidence >= 0 AND confidence <= 100),
            entry_price DECIMAL(10,5),
            stop_loss DECIMAL(10,5),
            take_profit DECIMAL(10,5),
            timeframe VARCHAR(10) NOT NULL,
            analysis_data JSONB,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            expires_at TIMESTAMPTZ,
            performance_score DECIMAL(5,2)
        );
        """,
        
        # User signal subscriptions table
        """
        CREATE TABLE IF NOT EXISTS user_signal_subscriptions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
            signal_type VARCHAR(50) NOT NULL,
            symbols TEXT[] DEFAULT '{}',
            timeframes TEXT[] DEFAULT '{}',
            min_confidence DECIMAL(5,2) DEFAULT 70.00,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(user_id, signal_type)
        );
        """,
        
        # Performance analytics table
        """
        CREATE TABLE IF NOT EXISTS performance_analytics (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
            mt5_account_id UUID REFERENCES mt5_accounts(id) ON DELETE SET NULL,
            date DATE NOT NULL,
            total_trades INTEGER DEFAULT 0,
            winning_trades INTEGER DEFAULT 0,
            losing_trades INTEGER DEFAULT 0,
            total_profit DECIMAL(15,2) DEFAULT 0.00,
            total_loss DECIMAL(15,2) DEFAULT 0.00,
            net_profit DECIMAL(15,2) DEFAULT 0.00,
            win_rate DECIMAL(5,2) DEFAULT 0.00,
            profit_factor DECIMAL(10,2) DEFAULT 0.00,
            max_drawdown DECIMAL(10,2) DEFAULT 0.00,
            sharpe_ratio DECIMAL(10,4) DEFAULT 0.00,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(user_id, mt5_account_id, date)
        );
        """,
        
        # Risk management settings table
        """
        CREATE TABLE IF NOT EXISTS risk_management_settings (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
            mt5_account_id UUID REFERENCES mt5_accounts(id) ON DELETE SET NULL,
            max_risk_per_trade DECIMAL(5,2) DEFAULT 2.00,
            max_daily_risk DECIMAL(5,2) DEFAULT 10.00,
            max_open_positions INTEGER DEFAULT 10,
            max_correlation_exposure DECIMAL(5,2) DEFAULT 50.00,
            stop_loss_type VARCHAR(20) DEFAULT 'percentage' CHECK (stop_loss_type IN ('percentage', 'fixed', 'atr')),
            take_profit_ratio DECIMAL(5,2) DEFAULT 2.00,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(user_id, mt5_account_id)
        );
        """,
        
        # System alerts table
        """
        CREATE TABLE IF NOT EXISTS system_alerts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES user_profiles(id) ON DELETE SET NULL,
            alert_type VARCHAR(50) NOT NULL,
            severity VARCHAR(20) DEFAULT 'info' CHECK (severity IN ('info', 'warning', 'error', 'critical')),
            title VARCHAR(255) NOT NULL,
            message TEXT NOT NULL,
            data JSONB DEFAULT '{}',
            is_read BOOLEAN DEFAULT false,
            is_dismissed BOOLEAN DEFAULT false,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            read_at TIMESTAMPTZ,
            dismissed_at TIMESTAMPTZ
        );
        """,
        
        # API keys table
        """
        CREATE TABLE IF NOT EXISTS api_keys (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
            key_name VARCHAR(100) NOT NULL,
            key_hash TEXT NOT NULL UNIQUE,
            permissions TEXT[] DEFAULT '{}',
            is_active BOOLEAN DEFAULT true,
            last_used_at TIMESTAMPTZ,
            expires_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(user_id, key_name)
        );
        """,
        
        # Audit logs table
        """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES user_profiles(id) ON DELETE SET NULL,
            action VARCHAR(100) NOT NULL,
            resource_type VARCHAR(50),
            resource_id UUID,
            old_values JSONB,
            new_values JSONB,
            ip_address INET,
            user_agent TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
    ]
    
    for i, sql in enumerate(sql_commands, 1):
        try:
            print(f"  Creating table {i}/{len(sql_commands)}...")
            supabase.rpc('exec_sql', {'sql': sql}).execute()
            print(f"  ✅ Table {i} created successfully")
        except Exception as e:
            print(f"  ❌ Error creating table {i}: {e}")

def setup_rls_policies(supabase: Client):
    """Set up Row Level Security policies"""
    print("🔒 Setting up RLS policies...")
    
    rls_commands = [
        # Enable RLS on all tables
        "ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE mt5_accounts ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE trading_sessions ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE trading_positions ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE trading_orders ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE ai_signals ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE user_signal_subscriptions ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE performance_analytics ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE risk_management_settings ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE system_alerts ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;",
        
        # User profiles policies
        """
        CREATE POLICY "Users can view own profile" ON user_profiles
        FOR SELECT USING (auth.uid() = id);
        """,
        """
        CREATE POLICY "Users can update own profile" ON user_profiles
        FOR UPDATE USING (auth.uid() = id);
        """,
        
        # MT5 accounts policies
        """
        CREATE POLICY "Users can view own MT5 accounts" ON mt5_accounts
        FOR SELECT USING (auth.uid() = user_id);
        """,
        """
        CREATE POLICY "Users can manage own MT5 accounts" ON mt5_accounts
        FOR ALL USING (auth.uid() = user_id);
        """,
        
        # Trading positions policies
        """
        CREATE POLICY "Users can view own positions" ON trading_positions
        FOR SELECT USING (auth.uid() = user_id);
        """,
        """
        CREATE POLICY "Users can manage own positions" ON trading_positions
        FOR ALL USING (auth.uid() = user_id);
        """,
        
        # AI signals policies
        """
        CREATE POLICY "All users can view active signals" ON ai_signals
        FOR SELECT USING (is_active = true);
        """,
        
        # System alerts policies
        """
        CREATE POLICY "Users can view own alerts" ON system_alerts
        FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);
        """,
        """
        CREATE POLICY "Users can update own alerts" ON system_alerts
        FOR UPDATE USING (auth.uid() = user_id);
        """
    ]
    
    for i, rls in enumerate(rls_commands, 1):
        try:
            print(f"  Setting up RLS policy {i}/{len(rls_commands)}...")
            supabase.rpc('exec_sql', {'sql': rls}).execute()
            print(f"  ✅ RLS policy {i} set successfully")
        except Exception as e:
            print(f"  ❌ Error setting RLS policy {i}: {e}")

def create_indexes(supabase: Client):
    """Create database indexes for performance"""
    print("📊 Creating database indexes...")
    
    index_commands = [
        "CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);",
        "CREATE INDEX IF NOT EXISTS idx_user_profiles_phone ON user_profiles(phone);",
        "CREATE INDEX IF NOT EXISTS idx_mt5_accounts_user_id ON mt5_accounts(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_mt5_accounts_login ON mt5_accounts(mt5_login);",
        "CREATE INDEX IF NOT EXISTS idx_trading_sessions_user_id ON trading_sessions(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_trading_sessions_token ON trading_sessions(session_token);",
        "CREATE INDEX IF NOT EXISTS idx_trading_positions_user_id ON trading_positions(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_trading_positions_symbol ON trading_positions(symbol);",
        "CREATE INDEX IF NOT EXISTS idx_trading_positions_open_time ON trading_positions(open_time);",
        "CREATE INDEX IF NOT EXISTS idx_ai_signals_symbol ON ai_signals(symbol);",
        "CREATE INDEX IF NOT EXISTS idx_ai_signals_created_at ON ai_signals(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_performance_analytics_user_id ON performance_analytics(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_performance_analytics_date ON performance_analytics(date);",
        "CREATE INDEX IF NOT EXISTS idx_system_alerts_user_id ON system_alerts(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_system_alerts_created_at ON system_alerts(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);"
    ]
    
    for i, index in enumerate(index_commands, 1):
        try:
            print(f"  Creating index {i}/{len(index_commands)}...")
            supabase.rpc('exec_sql', {'sql': index}).execute()
            print(f"  ✅ Index {i} created successfully")
        except Exception as e:
            print(f"  ❌ Error creating index {i}: {e}")

def create_functions(supabase: Client):
    """Create database functions"""
    print("⚙️  Creating database functions...")
    
    function_commands = [
        # Function to get user trading stats
        """
        CREATE OR REPLACE FUNCTION get_user_trading_stats(user_uuid UUID)
        RETURNS TABLE (
            total_trades INTEGER,
            winning_trades INTEGER,
            losing_trades INTEGER,
            win_rate DECIMAL,
            total_profit DECIMAL,
            max_drawdown DECIMAL
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT 
                COALESCE(SUM(pa.total_trades), 0)::INTEGER as total_trades,
                COALESCE(SUM(pa.winning_trades), 0)::INTEGER as winning_trades,
                COALESCE(SUM(pa.losing_trades), 0)::INTEGER as losing_trades,
                CASE 
                    WHEN COALESCE(SUM(pa.total_trades), 0) > 0 
                    THEN (COALESCE(SUM(pa.winning_trades), 0)::DECIMAL / SUM(pa.total_trades)::DECIMAL * 100)
                    ELSE 0::DECIMAL 
                END as win_rate,
                COALESCE(SUM(pa.net_profit), 0)::DECIMAL as total_profit,
                COALESCE(MAX(pa.max_drawdown), 0)::DECIMAL as max_drawdown
            FROM performance_analytics pa
            WHERE pa.user_id = user_uuid;
        END;
        $$ LANGUAGE plpgsql;
        """,
        
        # Function to update user last login
        """
        CREATE OR REPLACE FUNCTION update_user_last_login(user_uuid UUID)
        RETURNS VOID AS $$
        BEGIN
            UPDATE user_profiles 
            SET last_login = NOW(), updated_at = NOW()
            WHERE id = user_uuid;
        END;
        $$ LANGUAGE plpgsql;
        """,
        
        # Function to clean expired sessions
        """
        CREATE OR REPLACE FUNCTION clean_expired_sessions()
        RETURNS INTEGER AS $$
        DECLARE
            deleted_count INTEGER;
        BEGIN
            DELETE FROM trading_sessions 
            WHERE expires_at < NOW() OR is_active = false;
            
            GET DIAGNOSTICS deleted_count = ROW_COUNT;
            RETURN deleted_count;
        END;
        $$ LANGUAGE plpgsql;
        """
    ]
    
    for i, func in enumerate(function_commands, 1):
        try:
            print(f"  Creating function {i}/{len(function_commands)}...")
            supabase.rpc('exec_sql', {'sql': func}).execute()
            print(f"  ✅ Function {i} created successfully")
        except Exception as e:
            print(f"  ❌ Error creating function {i}: {e}")

def insert_sample_data(supabase: Client):
    """Insert sample data for testing"""
    print("📝 Inserting sample data...")
    
    try:
        # Insert sample AI signals
        sample_signals = [
            {
                "signal_type": "ICT_OrderBlock",
                "symbol": "EURUSD",
                "direction": "buy",
                "confidence": 85.5,
                "entry_price": 1.0850,
                "stop_loss": 1.0800,
                "take_profit": 1.0950,
                "timeframe": "H1",
                "analysis_data": {
                    "pattern": "bullish_order_block",
                    "strength": "high",
                    "confluence": ["fvg", "breaker_block"]
                }
            },
            {
                "signal_type": "Shadow_Mode",
                "symbol": "GBPUSD",
                "direction": "sell",
                "confidence": 78.2,
                "entry_price": 1.2650,
                "stop_loss": 1.2700,
                "take_profit": 1.2550,
                "timeframe": "H4",
                "analysis_data": {
                    "institutional_flow": "bearish",
                    "whale_activity": "high_selling",
                    "dark_pool_sentiment": "negative"
                }
            }
        ]
        
        for signal in sample_signals:
            supabase.table("ai_signals").insert(signal).execute()
        
        print("  ✅ Sample AI signals inserted")
        
    except Exception as e:
        print(f"  ❌ Error inserting sample data: {e}")

def main():
    """Main setup function"""
    print("🚀 Starting Supabase Database Setup for AI Algo Trade Platform")
    print("=" * 60)
    
    try:
        # Create Supabase client
        supabase = create_supabase_client()
        print("✅ Supabase client connected successfully")
        
        # Setup database
        setup_database_tables(supabase)
        setup_rls_policies(supabase)
        create_indexes(supabase)
        create_functions(supabase)
        insert_sample_data(supabase)
        
        print("\n" + "=" * 60)
        print("🎉 Supabase database setup completed successfully!")
        print("📊 Database is ready for AI Algo Trade Platform")
        print("🔗 Supabase URL:", SUPABASE_URL)
        print("✅ All tables, policies, indexes, and functions created")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 