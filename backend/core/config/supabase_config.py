import os
from typing import Optional
from supabase import create_client, Client
from supabase.client import ClientOptions
import logging

logger = logging.getLogger(__name__)

class SupabaseConfig:
    def __init__(self):
        # Supabase credentials
        self.url = "https://jregdcopqylriziucooi.supabase.co"
        self.service_role_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpyZWdkY29wcXlscml6aXVjb29pIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTMzNDA5MywiZXhwIjoyMDY2OTEwMDkzfQ.C2UERKNzoHL_TBmO9nt5iFgbp1m-70KaJu38QFyY1VY"
        
        # Get anon key from environment or use service role for development
        self.anon_key = os.getenv("SUPABASE_ANON_KEY", self.service_role_key)
        
    def get_client(self, use_service_role: bool = False) -> Client:
        """Get Supabase client"""
        try:
            key = self.service_role_key if use_service_role else self.anon_key
            
            options = ClientOptions(
                auto_refresh_token=True,
                persist_session=True,
                detect_session_in_url=True,
                headers={
                    "Authorization": f"Bearer {key}",
                    "apikey": key
                }
            )
            
            client = create_client(self.url, key, options)
            logger.info("Supabase client created successfully")
            return client
            
        except Exception as e:
            logger.error(f"Failed to create Supabase client: {e}")
            raise
    
    def get_admin_client(self) -> Client:
        """Get Supabase admin client with service role"""
        return self.get_client(use_service_role=True)
    
    def get_public_client(self) -> Client:
        """Get Supabase public client"""
        return self.get_client(use_service_role=False)

# Global instance
supabase_config = SupabaseConfig()

# Helper functions
def get_supabase_client() -> Client:
    """Get default Supabase client"""
    return supabase_config.get_public_client()

def get_supabase_admin() -> Client:
    """Get Supabase admin client"""
    return supabase_config.get_admin_client() 