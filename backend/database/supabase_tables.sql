-- AI Algo Trade Platform - Supabase Database Schema
-- Execute these SQL commands in Supabase SQL Editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- User Profiles Table
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    full_name VARCHAR(255),
    avatar_url TEXT,
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('user', 'premium', 'admin')),
    subscription_plan VARCHAR(50) DEFAULT 'free' CHECK (subscription_plan IN ('free', 'basic', 'premium', 'enterprise')),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    trading_preferences JSONB DEFAULT '{}',
    api_settings JSONB DEFAULT '{}',
    notification_preferences JSONB DEFAULT '{
        "email_notifications": true,
        "sms_notifications": false,
        "push_notifications": true,
        "trading_alerts": true,
        "market_updates": true
    }'
);

-- MT5 Accounts Table
CREATE TABLE IF NOT EXISTS mt5_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    mt5_login VARCHAR(50) NOT NULL,
    mt5_server VARCHAR(100) NOT NULL,
    mt5_password_encrypted TEXT NOT NULL,
    account_type VARCHAR(50) DEFAULT 'unknown',
    currency VARCHAR(10) DEFAULT 'USD',
    balance DECIMAL(15,2) DEFAULT 0.00,
    equity DECIMAL(15,2) DEFAULT 0.00,
    margin DECIMAL(15,2) DEFAULT 0.00,
    free_margin DECIMAL(15,2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_sync TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(mt5_login, mt5_server)
);

-- Trading Sessions Table
CREATE TABLE IF NOT EXISTS trading_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    session_token VARCHAR(255) NOT NULL,
    login_method VARCHAR(50) NOT NULL CHECK (login_method IN ('email', 'phone', 'mt5')),
    ip_address INET,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() + INTERVAL '24 hours',
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trading Positions Table
CREATE TABLE IF NOT EXISTS trading_positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    mt5_account_id UUID REFERENCES mt5_accounts(id) ON DELETE CASCADE,
    ticket BIGINT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    position_type VARCHAR(10) NOT NULL CHECK (position_type IN ('BUY', 'SELL')),
    volume DECIMAL(10,2) NOT NULL,
    open_price DECIMAL(15,5) NOT NULL,
    current_price DECIMAL(15,5),
    stop_loss DECIMAL(15,5),
    take_profit DECIMAL(15,5),
    profit DECIMAL(15,2) DEFAULT 0.00,
    commission DECIMAL(15,2) DEFAULT 0.00,
    swap DECIMAL(15,2) DEFAULT 0.00,
    comment TEXT,
    magic_number BIGINT,
    open_time TIMESTAMP WITH TIME ZONE NOT NULL,
    close_time TIMESTAMP WITH TIME ZONE,
    is_open BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trading Orders Table
CREATE TABLE IF NOT EXISTS trading_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    mt5_account_id UUID REFERENCES mt5_accounts(id) ON DELETE CASCADE,
    ticket BIGINT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    order_type VARCHAR(20) NOT NULL,
    volume DECIMAL(10,2) NOT NULL,
    price DECIMAL(15,5) NOT NULL,
    stop_loss DECIMAL(15,5),
    take_profit DECIMAL(15,5),
    comment TEXT,
    magic_number BIGINT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'filled', 'cancelled', 'rejected')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    filled_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE
);

-- AI Signals Table
CREATE TABLE IF NOT EXISTS ai_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    signal_type VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('BUY', 'SELL')),
    confidence DECIMAL(5,2) NOT NULL CHECK (confidence >= 0 AND confidence <= 100),
    entry_price DECIMAL(15,5),
    stop_loss DECIMAL(15,5),
    take_profit DECIMAL(15,5),
    timeframe VARCHAR(10) NOT NULL,
    analysis_data JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    performance_score DECIMAL(5,2)
);

-- User Signal Subscriptions Table
CREATE TABLE IF NOT EXISTS user_signal_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    signal_type VARCHAR(50) NOT NULL,
    symbols TEXT[] DEFAULT '{}',
    timeframes TEXT[] DEFAULT '{}',
    min_confidence DECIMAL(5,2) DEFAULT 70.00,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance Analytics Table
CREATE TABLE IF NOT EXISTS performance_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    mt5_account_id UUID REFERENCES mt5_accounts(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    total_profit DECIMAL(15,2) DEFAULT 0.00,
    total_loss DECIMAL(15,2) DEFAULT 0.00,
    net_profit DECIMAL(15,2) DEFAULT 0.00,
    win_rate DECIMAL(5,2) DEFAULT 0.00,
    profit_factor DECIMAL(8,2) DEFAULT 0.00,
    max_drawdown DECIMAL(15,2) DEFAULT 0.00,
    sharpe_ratio DECIMAL(8,4) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, mt5_account_id, date)
);

-- Risk Management Settings Table
CREATE TABLE IF NOT EXISTS risk_management_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    mt5_account_id UUID REFERENCES mt5_accounts(id) ON DELETE CASCADE,
    max_risk_per_trade DECIMAL(5,2) DEFAULT 2.00,
    max_daily_risk DECIMAL(5,2) DEFAULT 10.00,
    max_open_positions INTEGER DEFAULT 5,
    max_correlation_exposure DECIMAL(5,2) DEFAULT 30.00,
    stop_loss_type VARCHAR(20) DEFAULT 'percentage' CHECK (stop_loss_type IN ('fixed', 'percentage', 'atr')),
    take_profit_ratio DECIMAL(5,2) DEFAULT 2.00,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- System Alerts Table
CREATE TABLE IF NOT EXISTS system_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) DEFAULT 'info' CHECK (severity IN ('info', 'warning', 'error', 'critical')),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    data JSONB DEFAULT '{}',
    is_read BOOLEAN DEFAULT false,
    is_dismissed BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE,
    dismissed_at TIMESTAMP WITH TIME ZONE
);

-- API Keys Table
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    key_name VARCHAR(100) NOT NULL,
    key_hash VARCHAR(255) NOT NULL UNIQUE,
    permissions TEXT[] DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    last_used_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit Logs Table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES user_profiles(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_user_profiles_phone ON user_profiles(phone);
CREATE INDEX IF NOT EXISTS idx_user_profiles_role ON user_profiles(role);
CREATE INDEX IF NOT EXISTS idx_user_profiles_created_at ON user_profiles(created_at);

CREATE INDEX IF NOT EXISTS idx_mt5_accounts_user_id ON mt5_accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_mt5_accounts_login_server ON mt5_accounts(mt5_login, mt5_server);
CREATE INDEX IF NOT EXISTS idx_mt5_accounts_is_active ON mt5_accounts(is_active);

CREATE INDEX IF NOT EXISTS idx_trading_sessions_user_id ON trading_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_trading_sessions_token ON trading_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_trading_sessions_active ON trading_sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_trading_sessions_expires ON trading_sessions(expires_at);

CREATE INDEX IF NOT EXISTS idx_trading_positions_user_id ON trading_positions(user_id);
CREATE INDEX IF NOT EXISTS idx_trading_positions_mt5_account ON trading_positions(mt5_account_id);
CREATE INDEX IF NOT EXISTS idx_trading_positions_symbol ON trading_positions(symbol);
CREATE INDEX IF NOT EXISTS idx_trading_positions_open ON trading_positions(is_open);
CREATE INDEX IF NOT EXISTS idx_trading_positions_open_time ON trading_positions(open_time);

CREATE INDEX IF NOT EXISTS idx_ai_signals_symbol ON ai_signals(symbol);
CREATE INDEX IF NOT EXISTS idx_ai_signals_type ON ai_signals(signal_type);
CREATE INDEX IF NOT EXISTS idx_ai_signals_active ON ai_signals(is_active);
CREATE INDEX IF NOT EXISTS idx_ai_signals_created_at ON ai_signals(created_at);

CREATE INDEX IF NOT EXISTS idx_performance_analytics_user_id ON performance_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_performance_analytics_date ON performance_analytics(date);
CREATE INDEX IF NOT EXISTS idx_performance_analytics_mt5_account ON performance_analytics(mt5_account_id);

CREATE INDEX IF NOT EXISTS idx_system_alerts_user_id ON system_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_system_alerts_type ON system_alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_system_alerts_severity ON system_alerts(severity);
CREATE INDEX IF NOT EXISTS idx_system_alerts_read ON system_alerts(is_read);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at triggers to relevant tables
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mt5_accounts_updated_at BEFORE UPDATE ON mt5_accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_trading_positions_updated_at BEFORE UPDATE ON trading_positions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_trading_orders_updated_at BEFORE UPDATE ON trading_orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_risk_management_settings_updated_at BEFORE UPDATE ON risk_management_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) Policies
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE mt5_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE trading_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE trading_positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE trading_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_signal_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE performance_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE risk_management_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;

-- Policies for user_profiles
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = id);

-- Policies for mt5_accounts
CREATE POLICY "Users can view own MT5 accounts" ON mt5_accounts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own MT5 accounts" ON mt5_accounts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own MT5 accounts" ON mt5_accounts
    FOR UPDATE USING (auth.uid() = user_id);

-- Policies for trading_positions
CREATE POLICY "Users can view own positions" ON trading_positions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own positions" ON trading_positions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own positions" ON trading_positions
    FOR UPDATE USING (auth.uid() = user_id);

-- Policies for trading_orders
CREATE POLICY "Users can view own orders" ON trading_orders
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own orders" ON trading_orders
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own orders" ON trading_orders
    FOR UPDATE USING (auth.uid() = user_id);

-- Policies for system_alerts
CREATE POLICY "Users can view own alerts" ON system_alerts
    FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);

CREATE POLICY "Users can update own alerts" ON system_alerts
    FOR UPDATE USING (auth.uid() = user_id);

-- Admin policies (for service role)
CREATE POLICY "Service role can do everything" ON user_profiles
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can do everything on mt5_accounts" ON mt5_accounts
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can do everything on trading_positions" ON trading_positions
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can do everything on trading_orders" ON trading_orders
    FOR ALL USING (auth.role() = 'service_role');

-- Insert demo data
INSERT INTO user_profiles (id, email, full_name, role, subscription_plan, is_verified) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'admin@aialgotrade.com', 'Admin User', 'admin', 'enterprise', true),
('550e8400-e29b-41d4-a716-446655440001', 'demo@aialgotrade.com', 'Demo User', 'user', 'free', true)
ON CONFLICT (id) DO NOTHING;

INSERT INTO mt5_accounts (user_id, mt5_login, mt5_server, mt5_password_encrypted, account_type, currency, balance) VALUES
('550e8400-e29b-41d4-a716-446655440001', '25201110', 'Tickmill-Demo', 'encrypted_password_here', 'Demo', 'USD', 10000.00)
ON CONFLICT (mt5_login, mt5_server) DO NOTHING;

-- Create functions for common operations
CREATE OR REPLACE FUNCTION get_user_trading_stats(user_uuid UUID)
RETURNS TABLE(
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
            THEN (COALESCE(SUM(pa.winning_trades), 0) * 100.0 / COALESCE(SUM(pa.total_trades), 1))::DECIMAL(5,2)
            ELSE 0.00::DECIMAL(5,2)
        END as win_rate,
        COALESCE(SUM(pa.net_profit), 0.00)::DECIMAL(15,2) as total_profit,
        COALESCE(MIN(pa.max_drawdown), 0.00)::DECIMAL(15,2) as max_drawdown
    FROM performance_analytics pa
    WHERE pa.user_id = user_uuid;
END;
$$ LANGUAGE plpgsql; 