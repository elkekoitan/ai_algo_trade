'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
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
  Loader2,
  Zap,
  Shield,
  TrendingUp,
  Brain,
  Sparkles,
  ArrowRight,
  Globe
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { useAuth } from '@/components/auth/AuthProvider'
import { useRouter } from 'next/navigation'

export default function LoginPage() {
  const router = useRouter()
  const { loginWithEmail, loginWithPhone, loginWithMT5, loading, isAuthenticated } = useAuth()
  
  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      router.push('/')
    }
  }, [isAuthenticated, router])

  // Form states
  const [activeTab, setActiveTab] = useState('mt5')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isAnimating, setIsAnimating] = useState(false)

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

  // MT5 login state - Pre-fill with demo account
  const [mt5Form, setMt5Form] = useState({
    login: '25201110',
    password: 'e|([rXU1IsiM',
    server: 'Tickmill-Demo'
  })

  // Demo account quick login
  const handleDemoLogin = async () => {
    setError('')
    setSuccess('')
    setIsAnimating(true)

    try {
      await loginWithMT5(mt5Form.login, mt5Form.password, mt5Form.server)
      setSuccess('Demo hesabına giriş başarılı!')
      setTimeout(() => router.push('/'), 1500)
    } catch (error: any) {
      setError(error.message || 'Demo girişi başarısız')
    } finally {
      setIsAnimating(false)
    }
  }

  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    if (!emailForm.email || !emailForm.password) {
      setError('Lütfen tüm alanları doldurun')
      return
    }

    try {
      await loginWithEmail(emailForm.email, emailForm.password)
      setSuccess('Giriş başarılı!')
      setTimeout(() => router.push('/'), 1500)
    } catch (error: any) {
      setError(error.message || 'Giriş başarısız')
    }
  }

  const handlePhoneLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    if (!phoneForm.phone || !phoneForm.password) {
      setError('Lütfen tüm alanları doldurun')
      return
    }

    try {
      await loginWithPhone(phoneForm.phone, phoneForm.password)
      setSuccess('Giriş başarılı!')
      setTimeout(() => router.push('/'), 1500)
    } catch (error: any) {
      setError(error.message || 'Telefon girişi başarısız')
    }
  }

  const handleMT5Login = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    if (!mt5Form.login || !mt5Form.password || !mt5Form.server) {
      setError('Lütfen tüm MT5 alanlarını doldurun')
      return
    }

    try {
      await loginWithMT5(mt5Form.login, mt5Form.password, mt5Form.server)
      setSuccess('MT5 girişi başarılı!')
      setTimeout(() => router.push('/'), 1500)
    } catch (error: any) {
      setError(error.message || 'MT5 girişi başarısız')
    }
  }

  const TabButton = ({ id, icon: Icon, label, isActive, onClick }: any) => (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className={`relative flex items-center justify-center px-6 py-3 rounded-xl transition-all duration-300 ${
        isActive 
          ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg shadow-blue-500/25' 
          : 'bg-gray-800/50 text-gray-400 hover:text-white hover:bg-gray-700/50'
      }`}
    >
      <Icon className="h-4 w-4 mr-2" />
      <span className="font-medium">{label}</span>
      {isActive && (
        <motion.div
          layoutId="activeTab"
          className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl"
          style={{ zIndex: -1 }}
          transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
        />
      )}
    </motion.button>
  )

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]"></div>
        <motion.div
          animate={{
            backgroundPosition: ['0% 0%', '100% 100%'],
          }}
          transition={{
            duration: 20,
            ease: 'linear',
            repeat: Infinity,
          }}
          className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10"
        />
      </div>

      {/* Floating Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-4 h-4 bg-blue-400/20 rounded-full"
            animate={{
              x: [0, 100, 0],
              y: [0, -100, 0],
            }}
            transition={{
              duration: 10 + i * 2,
              repeat: Infinity,
              ease: 'linear',
            }}
            style={{
              left: `${10 + i * 15}%`,
              top: `${20 + i * 10}%`,
            }}
          />
        ))}
      </div>

      <div className="relative z-10 flex min-h-screen">
        {/* Left Side - Branding */}
        <div className="hidden lg:flex lg:w-1/2 flex-col justify-center items-center p-12">
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <div className="mb-8">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
                className="inline-block"
              >
                <div className="w-24 h-24 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mb-6 shadow-xl shadow-blue-500/25">
                  <Brain className="h-12 w-12 text-white" />
                </div>
              </motion.div>
            </div>

            <h1 className="text-5xl font-bold text-white mb-4 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              AI Algo Trade
            </h1>
            
            <p className="text-xl text-gray-300 mb-8 max-w-md">
              Yapay zeka destekli algoritmik ticaretin geleceği
            </p>

            {/* Features */}
            <div className="space-y-4">
              {[
                { icon: Zap, text: 'Şimşek hızında işlem' },
                { icon: Shield, text: 'Askeri düzey güvenlik' },
                { icon: TrendingUp, text: 'Gelişmiş analitik' },
                { icon: Globe, text: 'Global piyasa erişimi' }
              ].map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 + index * 0.1 }}
                  className="flex items-center text-gray-300"
                >
                  <feature.icon className="h-5 w-5 text-blue-400 mr-3" />
                  <span>{feature.text}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Right Side - Login Form */}
        <div className="w-full lg:w-1/2 flex items-center justify-center p-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="w-full max-w-md"
          >
            {/* Quick Demo Access */}
            <div className="mb-8">
              <motion.div
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="bg-gradient-to-r from-emerald-500/10 to-blue-500/10 border border-emerald-500/20 rounded-xl p-4 cursor-pointer"
                onClick={handleDemoLogin}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-emerald-400 font-semibold flex items-center">
                      <Sparkles className="h-4 w-4 mr-2" />
                      Hızlı Demo Giriş
                    </h3>
                    <p className="text-sm text-gray-400 mt-1">
                      Tickmill demo hesabı ile dene
                    </p>
                  </div>
                  <ArrowRight className="h-5 w-5 text-emerald-400" />
                </div>
                {isAnimating && (
                  <div className="mt-2 flex items-center text-emerald-400">
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    <span className="text-sm">Demo hesabına bağlanıyor...</span>
                  </div>
                )}
              </motion.div>
            </div>

            {/* Login Card */}
            <Card className="bg-black/40 border-gray-700 backdrop-blur-xl shadow-2xl">
              <CardContent className="p-8">
                <div className="text-center mb-8">
                  <h2 className="text-3xl font-bold text-white mb-2">
                    Hoş Geldiniz
                  </h2>
                  <p className="text-gray-400">
                    Trading hesabınıza giriş yapın
                  </p>
                </div>

                {/* Tab Navigation */}
                <div className="flex space-x-2 mb-8 bg-gray-800/30 p-2 rounded-xl">
                  <TabButton
                    id="mt5"
                    icon={Server}
                    label="MT5"
                    isActive={activeTab === 'mt5'}
                    onClick={() => setActiveTab('mt5')}
                  />
                  <TabButton
                    id="email"
                    icon={Mail}
                    label="Email"
                    isActive={activeTab === 'email'}
                    onClick={() => setActiveTab('email')}
                  />
                  <TabButton
                    id="phone"
                    icon={Phone}
                    label="Telefon"
                    isActive={activeTab === 'phone'}
                    onClick={() => setActiveTab('phone')}
                  />
                </div>

                {/* Error/Success Messages */}
                <AnimatePresence>
                  {error && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="mb-4"
                    >
                      <Alert className="border-red-500 bg-red-500/10">
                        <AlertCircle className="h-4 w-4" />
                        <AlertDescription className="text-red-400">
                          {error}
                        </AlertDescription>
                      </Alert>
                    </motion.div>
                  )}

                  {success && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="mb-4"
                    >
                      <Alert className="border-green-500 bg-green-500/10">
                        <CheckCircle className="h-4 w-4" />
                        <AlertDescription className="text-green-400">
                          {success}
                        </AlertDescription>
                      </Alert>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Form Content */}
                <AnimatePresence mode="wait">
                  <motion.div
                    key={activeTab}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.3 }}
                  >
                    {/* MT5 Login (Default) */}
                    {activeTab === 'mt5' && (
                      <form onSubmit={handleMT5Login} className="space-y-6">
                        <div className="space-y-2">
                          <label className="text-sm font-medium text-gray-300">
                            MT5 Login ID
                          </label>
                          <div className="relative">
                            <User className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                            <Input
                              type="text"
                              placeholder="25201110"
                              value={mt5Form.login}
                              onChange={(e) => setMt5Form(prev => ({ ...prev, login: e.target.value }))}
                              className="pl-11 bg-gray-800/50 border-gray-600 text-white placeholder-gray-400 h-12 focus:border-blue-500 transition-colors"
                              required
                            />
                          </div>
                        </div>

                        <div className="space-y-2">
                          <label className="text-sm font-medium text-gray-300">
                            MT5 Şifresi
                          </label>
                          <div className="relative">
                            <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                            <Input
                              type={showPassword ? "text" : "password"}
                              placeholder="MT5 şifrenizi girin"
                              value={mt5Form.password}
                              onChange={(e) => setMt5Form(prev => ({ ...prev, password: e.target.value }))}
                              className="pl-11 pr-11 bg-gray-800/50 border-gray-600 text-white placeholder-gray-400 h-12 focus:border-blue-500 transition-colors"
                              required
                            />
                            <button
                              type="button"
                              onClick={() => setShowPassword(!showPassword)}
                              className="absolute right-3 top-3 text-gray-400 hover:text-white transition-colors"
                            >
                              {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                            </button>
                          </div>
                        </div>

                        <div className="space-y-2">
                          <label className="text-sm font-medium text-gray-300">
                            MT5 Sunucu
                          </label>
                          <div className="relative">
                            <Server className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                            <select
                              value={mt5Form.server}
                              onChange={(e) => setMt5Form(prev => ({ ...prev, server: e.target.value }))}
                              className="w-full pl-11 pr-4 py-3 bg-gray-800/50 border border-gray-600 rounded-xl text-white focus:outline-none focus:border-blue-500 transition-colors h-12"
                              required
                            >
                              <option value="Tickmill-Demo">Tickmill-Demo</option>
                              <option value="Tickmill-Live">Tickmill-Live</option>
                              <option value="MetaQuotes-Demo">MetaQuotes-Demo</option>
                            </select>
                          </div>
                        </div>

                        <div className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-xl p-4">
                          <h4 className="text-blue-400 font-semibold mb-2">Demo Hesap Bilgileri:</h4>
                          <div className="text-sm text-gray-300 space-y-1">
                            <p><span className="text-blue-400">Login:</span> 25201110</p>
                            <p><span className="text-blue-400">Şifre:</span> e|([rXU1IsiM</p>
                            <p><span className="text-blue-400">Sunucu:</span> Tickmill-Demo</p>
                          </div>
                        </div>

                        <Button
                          type="submit"
                          className="w-full h-12 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold rounded-xl transition-all duration-300 shadow-lg shadow-blue-500/25"
                          disabled={loading}
                        >
                          {loading ? (
                            <>
                              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                              MT5'e bağlanıyor...
                            </>
                          ) : (
                            <>
                              MT5 ile Giriş Yap
                              <ArrowRight className="ml-2 h-5 w-5" />
                            </>
                          )}
                        </Button>
                      </form>
                    )}

                    {/* Email Login */}
                    {activeTab === 'email' && (
                      <form onSubmit={handleEmailLogin} className="space-y-6">
                        <div className="space-y-2">
                          <label className="text-sm font-medium text-gray-300">
                            Email Adresi
                          </label>
                          <div className="relative">
                            <Mail className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                            <Input
                              type="email"
                              placeholder="Email adresinizi girin"
                              value={emailForm.email}
                              onChange={(e) => setEmailForm(prev => ({ ...prev, email: e.target.value }))}
                              className="pl-11 bg-gray-800/50 border-gray-600 text-white placeholder-gray-400 h-12 focus:border-blue-500 transition-colors"
                              required
                            />
                          </div>
                        </div>

                        <div className="space-y-2">
                          <label className="text-sm font-medium text-gray-300">
                            Şifre
                          </label>
                          <div className="relative">
                            <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                            <Input
                              type={showPassword ? "text" : "password"}
                              placeholder="Şifrenizi girin"
                              value={emailForm.password}
                              onChange={(e) => setEmailForm(prev => ({ ...prev, password: e.target.value }))}
                              className="pl-11 pr-11 bg-gray-800/50 border-gray-600 text-white placeholder-gray-400 h-12 focus:border-blue-500 transition-colors"
                              required
                            />
                            <button
                              type="button"
                              onClick={() => setShowPassword(!showPassword)}
                              className="absolute right-3 top-3 text-gray-400 hover:text-white transition-colors"
                            >
                              {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                            </button>
                          </div>
                        </div>

                        <Button
                          type="submit"
                          className="w-full h-12 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold rounded-xl transition-all duration-300 shadow-lg shadow-blue-500/25"
                          disabled={loading}
                        >
                          {loading ? (
                            <>
                              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                              Giriş yapılıyor...
                            </>
                          ) : (
                            <>
                              Email ile Giriş Yap
                              <ArrowRight className="ml-2 h-5 w-5" />
                            </>
                          )}
                        </Button>
                      </form>
                    )}

                    {/* Phone Login */}
                    {activeTab === 'phone' && (
                      <form onSubmit={handlePhoneLogin} className="space-y-6">
                        <div className="space-y-2">
                          <label className="text-sm font-medium text-gray-300">
                            Telefon Numarası
                          </label>
                          <div className="relative">
                            <Phone className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                            <Input
                              type="tel"
                              placeholder="+90 555 123 4567"
                              value={phoneForm.phone}
                              onChange={(e) => setPhoneForm(prev => ({ ...prev, phone: e.target.value }))}
                              className="pl-11 bg-gray-800/50 border-gray-600 text-white placeholder-gray-400 h-12 focus:border-blue-500 transition-colors"
                              required
                            />
                          </div>
                          <p className="text-xs text-gray-500">
                            Ülke kodunu dahil edin (örn: +90 Türkiye için)
                          </p>
                        </div>

                        <div className="space-y-2">
                          <label className="text-sm font-medium text-gray-300">
                            Şifre
                          </label>
                          <div className="relative">
                            <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                            <Input
                              type={showPassword ? "text" : "password"}
                              placeholder="Şifrenizi girin"
                              value={phoneForm.password}
                              onChange={(e) => setPhoneForm(prev => ({ ...prev, password: e.target.value }))}
                              className="pl-11 pr-11 bg-gray-800/50 border-gray-600 text-white placeholder-gray-400 h-12 focus:border-blue-500 transition-colors"
                              required
                            />
                            <button
                              type="button"
                              onClick={() => setShowPassword(!showPassword)}
                              className="absolute right-3 top-3 text-gray-400 hover:text-white transition-colors"
                            >
                              {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                            </button>
                          </div>
                        </div>

                        <Button
                          type="submit"
                          className="w-full h-12 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold rounded-xl transition-all duration-300 shadow-lg shadow-blue-500/25"
                          disabled={loading}
                        >
                          {loading ? (
                            <>
                              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                              Giriş yapılıyor...
                            </>
                          ) : (
                            <>
                              Telefon ile Giriş Yap
                              <ArrowRight className="ml-2 h-5 w-5" />
                            </>
                          )}
                        </Button>
                      </form>
                    )}
                  </motion.div>
                </AnimatePresence>

                {/* Footer Links */}
                <div className="mt-8 space-y-4">
                  <div className="text-center">
                    <button className="text-sm text-blue-400 hover:text-blue-300 transition-colors">
                      Şifrenizi mi unuttunuz?
                    </button>
                  </div>

                  <div className="text-center text-sm text-gray-400">
                    Hesabınız yok mu?{' '}
                    <button
                      onClick={() => router.push('/auth/register')}
                      className="text-blue-400 hover:text-blue-300 font-medium transition-colors"
                    >
                      Buradan kayıt olun
                    </button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  )
} 