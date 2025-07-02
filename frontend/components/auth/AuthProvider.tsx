'use client'

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { authAPI, tokenStorage, UserProfile, AuthResponse, SecureWebSocket } from '@/lib/supabase'

interface AuthContextType {
  user: UserProfile | null
  loading: boolean
  isAuthenticated: boolean
  websocket: SecureWebSocket | null
  
  // Authentication methods
  loginWithEmail: (email: string, password: string) => Promise<void>
  loginWithPhone: (phone: string, password: string) => Promise<void>
  loginWithMT5: (login: string, password: string, server: string) => Promise<void>
  
  // Registration methods
  registerWithEmail: (email: string, password: string, fullName?: string, phone?: string) => Promise<void>
  registerWithPhone: (phone: string, password: string, fullName?: string) => Promise<{ message: string; requires_verification: boolean }>
  verifyPhoneOTP: (phone: string, otp: string) => Promise<void>
  
  // Account management
  addMT5Account: (login: string, password: string, server: string) => Promise<void>
  getMT5Accounts: () => Promise<any>
  
  // Session management
  refreshSession: () => Promise<void>
  logout: () => Promise<void>
  
  // Password reset
  resetPasswordEmail: (email: string) => Promise<void>
  resetPasswordPhone: (phone: string) => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [websocket, setWebsocket] = useState<SecureWebSocket | null>(null)

  const isAuthenticated = !!user

  // Initialize auth state
  useEffect(() => {
    initializeAuth()
  }, [])

  // Setup WebSocket when user is authenticated
  useEffect(() => {
    if (user && !websocket) {
      setupWebSocket()
    } else if (!user && websocket) {
      websocket.disconnect()
      setWebsocket(null)
    }
  }, [user])

  const initializeAuth = async () => {
    try {
      const accessToken = tokenStorage.getAccessToken()
      const refreshToken = tokenStorage.getRefreshToken()
      const cachedUser = tokenStorage.getUserProfile()

      if (accessToken && cachedUser) {
        try {
          // Verify token is still valid
          const currentUser = await authAPI.getCurrentUser(accessToken)
          setUser(currentUser)
          tokenStorage.setUserProfile(currentUser)
        } catch (error) {
          // Token might be expired, try refresh
          if (refreshToken) {
            try {
              await refreshSession()
            } catch (refreshError) {
              // Refresh failed, clear tokens
              tokenStorage.clearTokens()
              setUser(null)
            }
          } else {
            tokenStorage.clearTokens()
            setUser(null)
          }
        }
      }
    } catch (error) {
      console.error('Auth initialization failed:', error)
    } finally {
      setLoading(false)
    }
  }

  const setupWebSocket = async () => {
    if (!user) return

    try {
      const accessToken = tokenStorage.getAccessToken()
      if (!accessToken) return

      const ws = new SecureWebSocket(user.id, accessToken)
      await ws.connect()
      
      // Subscribe to user-specific topics
      ws.subscribe('user_notifications')
      ws.subscribe('trading_signals')
      ws.subscribe('market_data')
      
      setWebsocket(ws)
    } catch (error) {
      console.error('WebSocket setup failed:', error)
    }
  }

  const handleAuthSuccess = (authResponse: AuthResponse) => {
    const { access_token, refresh_token, user: userData } = authResponse
    
    tokenStorage.setTokens(access_token, refresh_token)
    tokenStorage.setUserProfile(userData)
    setUser(userData)
  }

  const loginWithEmail = async (email: string, password: string) => {
    try {
      setLoading(true)
      const response = await authAPI.loginWithEmail(email, password)
      handleAuthSuccess(response)
    } catch (error) {
      throw error
    } finally {
      setLoading(false)
    }
  }

  const loginWithPhone = async (phone: string, password: string) => {
    try {
      setLoading(true)
      const response = await authAPI.loginWithPhone(phone, password)
      handleAuthSuccess(response)
    } catch (error) {
      throw error
    } finally {
      setLoading(false)
    }
  }

  const loginWithMT5 = async (login: string, password: string, server: string) => {
    try {
      setLoading(true)
      const response = await authAPI.loginWithMT5(login, password, server)
      handleAuthSuccess(response)
    } catch (error) {
      throw error
    } finally {
      setLoading(false)
    }
  }

  const registerWithEmail = async (email: string, password: string, fullName?: string, phone?: string) => {
    try {
      setLoading(true)
      const response = await authAPI.registerWithEmail(email, password, fullName, phone)
      handleAuthSuccess(response)
    } catch (error) {
      throw error
    } finally {
      setLoading(false)
    }
  }

  const registerWithPhone = async (phone: string, password: string, fullName?: string) => {
    try {
      setLoading(true)
      return await authAPI.registerWithPhone(phone, password, fullName)
    } catch (error) {
      throw error
    } finally {
      setLoading(false)
    }
  }

  const verifyPhoneOTP = async (phone: string, otp: string) => {
    try {
      setLoading(true)
      const response = await authAPI.verifyPhoneOTP(phone, otp)
      handleAuthSuccess(response)
    } catch (error) {
      throw error
    } finally {
      setLoading(false)
    }
  }

  const addMT5Account = async (login: string, password: string, server: string) => {
    const accessToken = tokenStorage.getAccessToken()
    if (!accessToken) throw new Error('Not authenticated')

    try {
      const response = await authAPI.addMT5Account(accessToken, login, password, server)
      
      // Refresh user profile to include new MT5 account
      const updatedUser = await authAPI.getCurrentUser(accessToken)
      setUser(updatedUser)
      tokenStorage.setUserProfile(updatedUser)
      
      return response
    } catch (error) {
      throw error
    }
  }

  const getMT5Accounts = async () => {
    const accessToken = tokenStorage.getAccessToken()
    if (!accessToken) throw new Error('Not authenticated')

    return await authAPI.getMT5Accounts(accessToken)
  }

  const refreshSession = async () => {
    const refreshToken = tokenStorage.getRefreshToken()
    if (!refreshToken) throw new Error('No refresh token available')

    try {
      const response = await authAPI.refreshToken(refreshToken)
      handleAuthSuccess(response)
    } catch (error) {
      // Refresh failed, clear tokens and redirect to login
      tokenStorage.clearTokens()
      setUser(null)
      throw error
    }
  }

  const logout = async () => {
    try {
      const accessToken = tokenStorage.getAccessToken()
      if (accessToken) {
        await authAPI.logout(accessToken)
      }
    } catch (error) {
      console.error('Logout API call failed:', error)
    } finally {
      // Always clear local state
      tokenStorage.clearTokens()
      setUser(null)
      
      if (websocket) {
        websocket.disconnect()
        setWebsocket(null)
      }
    }
  }

  const resetPasswordEmail = async (email: string) => {
    return await authAPI.resetPasswordEmail(email)
  }

  const resetPasswordPhone = async (phone: string) => {
    return await authAPI.resetPasswordPhone(phone)
  }

  // Auto-refresh token before expiration
  useEffect(() => {
    if (!user) return

    const refreshInterval = setInterval(async () => {
      try {
        await refreshSession()
      } catch (error) {
        console.error('Auto-refresh failed:', error)
        // Will be handled by refreshSession error handling
      }
    }, 25 * 60 * 1000) // Refresh every 25 minutes (tokens expire in 30 minutes)

    return () => clearInterval(refreshInterval)
  }, [user])

  const value: AuthContextType = {
    user,
    loading,
    isAuthenticated,
    websocket,
    loginWithEmail,
    loginWithPhone,
    loginWithMT5,
    registerWithEmail,
    registerWithPhone,
    verifyPhoneOTP,
    addMT5Account,
    getMT5Accounts,
    refreshSession,
    logout,
    resetPasswordEmail,
    resetPasswordPhone,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// Higher-order component for protected routes
export const withAuth = <P extends object>(
  Component: React.ComponentType<P>
): React.FC<P> => {
  return (props: P) => {
    const { isAuthenticated, loading } = useAuth()

    if (loading) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto mb-4"></div>
            <p className="text-white text-lg">Loading...</p>
          </div>
        </div>
      )
    }

    if (!isAuthenticated) {
      // Redirect to login page
      if (typeof window !== 'undefined') {
        window.location.href = '/auth/login'
      }
      return null
    }

    return <Component {...props} />
  }
}

// Hook for checking specific permissions
export const usePermissions = () => {
  const { user } = useAuth()

  const hasRole = (role: string): boolean => {
    return user?.role === role || user?.role === 'admin'
  }

  const hasSubscription = (plan: string): boolean => {
    if (!user) return false
    
    const planHierarchy = ['free', 'basic', 'premium', 'enterprise']
    const userPlanIndex = planHierarchy.indexOf(user.subscription_plan)
    const requiredPlanIndex = planHierarchy.indexOf(plan)
    
    return userPlanIndex >= requiredPlanIndex
  }

  const canAccessFeature = (feature: string): boolean => {
    if (!user) return false

    const featurePermissions: Record<string, string[]> = {
      'god_mode': ['premium', 'enterprise'],
      'shadow_mode': ['premium', 'enterprise'],
      'strategy_whisperer': ['basic', 'premium', 'enterprise'],
      'ai_mentor': ['premium', 'enterprise'],
      'social_trading': ['free', 'basic', 'premium', 'enterprise'],
      'multi_broker': ['premium', 'enterprise'],
      'advanced_analytics': ['premium', 'enterprise'],
      'api_access': ['basic', 'premium', 'enterprise']
    }

    const requiredPlans = featurePermissions[feature] || []
    return requiredPlans.includes(user.subscription_plan)
  }

  return {
    hasRole,
    hasSubscription,
    canAccessFeature,
    isAdmin: hasRole('admin'),
    isPremium: hasSubscription('premium'),
    isBasic: hasSubscription('basic')
  }
} 