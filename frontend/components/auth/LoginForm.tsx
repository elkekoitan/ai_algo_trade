'use client'

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Mail, 
  Phone, 
  Lock, 
  Eye, 
  EyeOff, 
  User, 
  Server,
  AlertCircle,
  CheckCircle,
  Loader2
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { useAuth } from './AuthProvider'
import { validateEmail, validatePhone } from '@/lib/supabase'

interface LoginFormProps {
  onSuccess?: () => void
  onSwitchToRegister?: () => void
}

export const LoginForm: React.FC<LoginFormProps> = ({ onSuccess, onSwitchToRegister }) => {
  const { loginWithEmail, loginWithPhone, loginWithMT5, loading } = useAuth()
  
  // Form states
  const [activeTab, setActiveTab] = useState('email')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Email login state
  const [emailForm, setEmailForm] = useState({
    email: '',
    password: ''
  })

  // Phone login state
  const [phoneForm, setPhoneForm] = useState({
    phone: '',
    password: ''
  })

  // MT5 login state
  const [mt5Form, setMt5Form] = useState({
    login: '',
    password: '',
    server: 'Tickmill-Demo'
  })

  const resetForm = () => {
    setError('')
    setSuccess('')
    setEmailForm({ email: '', password: '' })
    setPhoneForm({ phone: '', password: '' })
    setMt5Form({ login: '', password: '', server: 'Tickmill-Demo' })
  }

  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    // Validation
    if (!validateEmail(emailForm.email)) {
      setError('Please enter a valid email address')
      return
    }

    if (emailForm.password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }

    try {
      await loginWithEmail(emailForm.email, emailForm.password)
      setSuccess('Login successful!')
      onSuccess?.()
    } catch (error: any) {
      setError(error.message || 'Login failed')
    }
  }

  const handlePhoneLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    // Validation
    if (!validatePhone(phoneForm.phone)) {
      setError('Please enter a valid phone number')
      return
    }

    if (phoneForm.password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }

    try {
      await loginWithPhone(phoneForm.phone, phoneForm.password)
      setSuccess('Login successful!')
      onSuccess?.()
    } catch (error: any) {
      setError(error.message || 'Phone login failed')
    }
  }

  const handleMT5Login = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    // Validation
    if (!mt5Form.login || !mt5Form.password || !mt5Form.server) {
      setError('Please fill in all MT5 fields')
      return
    }

    try {
      await loginWithMT5(mt5Form.login, mt5Form.password, mt5Form.server)
      setSuccess('MT5 login successful!')
      onSuccess?.()
    } catch (error: any) {
      setError(error.message || 'MT5 login failed')
    }
  }

  return (
    <Card className="w-full max-w-md mx-auto bg-black/40 border-gray-700 backdrop-blur-sm">
      <CardHeader className="text-center">
        <CardTitle className="text-2xl font-bold text-white">
          Welcome Back
        </CardTitle>
        <p className="text-gray-400">
          Sign in to your AI Algo Trade account
        </p>
      </CardHeader>

      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3 bg-gray-800">
            <TabsTrigger value="email" className="data-[state=active]:bg-blue-600">
              <Mail className="h-4 w-4 mr-2" />
              Email
            </TabsTrigger>
            <TabsTrigger value="phone" className="data-[state=active]:bg-blue-600">
              <Phone className="h-4 w-4 mr-2" />
              Phone
            </TabsTrigger>
            <TabsTrigger value="mt5" className="data-[state=active]:bg-blue-600">
              <Server className="h-4 w-4 mr-2" />
              MT5
            </TabsTrigger>
          </TabsList>

          {/* Error/Success Messages */}
          {error && (
            <Alert className="mt-4 border-red-500 bg-red-500/10">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription className="text-red-400">
                {error}
              </AlertDescription>
            </Alert>
          )}

          {success && (
            <Alert className="mt-4 border-green-500 bg-green-500/10">
              <CheckCircle className="h-4 w-4" />
              <AlertDescription className="text-green-400">
                {success}
              </AlertDescription>
            </Alert>
          )}

          {/* Email Login */}
          <TabsContent value="email" className="mt-6">
            <form onSubmit={handleEmailLogin} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    type="email"
                    placeholder="Enter your email"
                    value={emailForm.email}
                    onChange={(e) => setEmailForm(prev => ({ ...prev, email: e.target.value }))}
                    className="pl-10 bg-gray-800 border-gray-600 text-white"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter your password"
                    value={emailForm.password}
                    onChange={(e) => setEmailForm(prev => ({ ...prev, password: e.target.value }))}
                    className="pl-10 pr-10 bg-gray-800 border-gray-600 text-white"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-3 text-gray-400 hover:text-white"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <Button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  'Sign in with Email'
                )}
              </Button>
            </form>
          </TabsContent>

          {/* Phone Login */}
          <TabsContent value="phone" className="mt-6">
            <form onSubmit={handlePhoneLogin} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300">
                  Phone Number
                </label>
                <div className="relative">
                  <Phone className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    type="tel"
                    placeholder="+1234567890"
                    value={phoneForm.phone}
                    onChange={(e) => setPhoneForm(prev => ({ ...prev, phone: e.target.value }))}
                    className="pl-10 bg-gray-800 border-gray-600 text-white"
                    required
                  />
                </div>
                <p className="text-xs text-gray-500">
                  Include country code (e.g., +1 for US)
                </p>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter your password"
                    value={phoneForm.password}
                    onChange={(e) => setPhoneForm(prev => ({ ...prev, password: e.target.value }))}
                    className="pl-10 pr-10 bg-gray-800 border-gray-600 text-white"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-3 text-gray-400 hover:text-white"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <Button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  'Sign in with Phone'
                )}
              </Button>
            </form>
          </TabsContent>

          {/* MT5 Login */}
          <TabsContent value="mt5" className="mt-6">
            <form onSubmit={handleMT5Login} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300">
                  MT5 Login
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    type="text"
                    placeholder="25201110"
                    value={mt5Form.login}
                    onChange={(e) => setMt5Form(prev => ({ ...prev, login: e.target.value }))}
                    className="pl-10 bg-gray-800 border-gray-600 text-white"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300">
                  MT5 Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter MT5 password"
                    value={mt5Form.password}
                    onChange={(e) => setMt5Form(prev => ({ ...prev, password: e.target.value }))}
                    className="pl-10 pr-10 bg-gray-800 border-gray-600 text-white"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-3 text-gray-400 hover:text-white"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300">
                  MT5 Server
                </label>
                <div className="relative">
                  <Server className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <select
                    value={mt5Form.server}
                    onChange={(e) => setMt5Form(prev => ({ ...prev, server: e.target.value }))}
                    className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="Tickmill-Demo">Tickmill-Demo</option>
                    <option value="Tickmill-Live">Tickmill-Live</option>
                    <option value="MetaQuotes-Demo">MetaQuotes-Demo</option>
                    <option value="Custom">Custom Server</option>
                  </select>
                </div>
              </div>

              {mt5Form.server === 'Custom' && (
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-300">
                    Custom Server
                  </label>
                  <Input
                    type="text"
                    placeholder="Enter server address"
                    value={mt5Form.server}
                    onChange={(e) => setMt5Form(prev => ({ ...prev, server: e.target.value }))}
                    className="bg-gray-800 border-gray-600 text-white"
                    required
                  />
                </div>
              )}

              <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3">
                <p className="text-xs text-blue-400">
                  <strong>Demo Account:</strong> Login: 25201110, Password: e|([rXU1IsiM, Server: Tickmill-Demo
                </p>
              </div>

              <Button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Connecting to MT5...
                  </>
                ) : (
                  'Sign in with MT5'
                )}
              </Button>
            </form>
          </TabsContent>
        </Tabs>

        {/* Footer Links */}
        <div className="mt-6 space-y-4">
          <div className="text-center">
            <button
              onClick={() => {/* TODO: Implement forgot password */}}
              className="text-sm text-blue-400 hover:text-blue-300"
            >
              Forgot your password?
            </button>
          </div>

          <div className="text-center text-sm text-gray-400">
            Don't have an account?{' '}
            <button
              onClick={onSwitchToRegister}
              className="text-blue-400 hover:text-blue-300 font-medium"
            >
              Sign up here
            </button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
} 