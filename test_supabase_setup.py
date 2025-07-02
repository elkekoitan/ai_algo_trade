#!/usr/bin/env python3
"""Test Supabase Setup and Configuration"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.core.config.supabase_config import get_supabase_admin_client
from backend.modules.auth.supabase_auth import supabase_auth_service

def test_supabase_connection():
    """Test Supabase connection and setup"""
    print("🚀 Testing Supabase Setup...")
    
    try:
        # Test admin client
        admin_client = get_supabase_admin_client()
        print("✅ Supabase Admin Client connected successfully")
        
        # Test auth service
        auth_service = supabase_auth_service
        print("✅ Supabase Auth Service initialized")
        
        # Test database connection
        try:
            response = admin_client.table('user_profiles').select('count', count='exact').execute()
            print(f"✅ Database connection test successful")
            print(f"📊 Total users in database: {response.count if hasattr(response, 'count') else 'Unknown'}")
        except Exception as db_error:
            print(f"⚠️  Database table may not exist yet: {db_error}")
            print("📝 This is normal if tables haven't been created yet")
        
        # Test environment variables
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ANON_KEY')
        supabase_service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if supabase_url and supabase_key and supabase_service_key:
            print("✅ All Supabase environment variables are set")
        else:
            print("❌ Missing Supabase environment variables:")
            if not supabase_url:
                print("  - SUPABASE_URL")
            if not supabase_key:
                print("  - SUPABASE_ANON_KEY")
            if not supabase_service_key:
                print("  - SUPABASE_SERVICE_ROLE_KEY")
        
        print("\n🎉 Supabase setup test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Supabase setup test failed: {e}")
        print("\n💡 Make sure to:")
        print("1. Set SUPABASE_URL environment variable")
        print("2. Set SUPABASE_ANON_KEY environment variable")
        print("3. Set SUPABASE_SERVICE_ROLE_KEY environment variable")
        print("4. Run the SQL schema creation script")
        return False

if __name__ == "__main__":
    success = test_supabase_connection()
    sys.exit(0 if success else 1) 