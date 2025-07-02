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
  AlertCircle,
  CheckCircle,
  Loader2,
  Zap,
  Shield,
  TrendingUp,
  Brain,
  ArrowRight,
  UserPlus
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { useAuth } from '@/components/auth/AuthProvider'
import { useRouter } from 'next/navigation'

export default function RegisterPage() {
  const router = useRouter()
  const { registerWithEmail, registerWithPhone, loading, isAuthenticated } = useAuth()
  
  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      router.push('/')
    }
  }, [isAuthenticated, router])

  // Form states
  const [activeTab, setActiveTab] = useState('email')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Email register state
  const [emailForm, setEmailForm] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
    phone: ''
  })

  // Phone register state
  const [phoneForm, setPhoneForm] = useState({
    phone: '',
    password: '',
    confirmPassword: '',
    fullName: ''
  })

  const handleEmailRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    // Validation
    if (!emailForm.email || !emailForm.password || !emailForm.confirmPassword) {
      setError('Lütfen tüm zorunlu alanları doldurun')
      return
    }

    if (emailForm.password !== emailForm.confirmPassword) {
      setError('Şifreler eşleşmiyor')
      return
    }

    if (emailForm.password.length < 8) {
      setError('Şifre en az 8 karakter olmalıdır')
      return
    }

    try {
      await registerWithEmail(
        emailForm.email, 
        emailForm.password, 
        emailForm.fullName || undefined,
        emailForm.phone || undefined
      )
      setSuccess('Kayıt başarılı! Hoş geldiniz!')
      setTimeout(() => router.push('/'), 1500)
    } catch (error: any) {
      setError(error.message || 'Kayıt başarısız')
    }
  }

  const handlePhoneRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    // Validation
    if (!phoneForm.phone || !phoneForm.password || !phoneForm.confirmPassword) {
      setError('Lütfen tüm zorunlu alanları doldurun')
      return
    }

    if (phoneForm.password !== phoneForm.confirmPassword) {
      setError('Şifreler eşleşmiyor')
      return
    }

    if (phoneForm.password.length < 8) {
      setError('Şifre en az 8 karakter olmalıdır')
      return
    }

    try {
      const result = await registerWithPhone(
        phoneForm.phone, 
        phoneForm.password, 
        phoneForm.fullName || undefined
      )
      
      if (result.requires_verification) {
        setSuccess('SMS doğrulama kodu gönderildi!')
        // You could redirect to OTP verification page here
      } else {
        setSuccess('Kayıt başarılı! Hoş geldiniz!')
        setTimeout(() => router.push('/'), 1500)
      }
    } catch (error: any) {
      setError(error.message || 'Telefon kaydı başarısız')
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
          layoutId="activeTabRegister"
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
        {[...Array(8)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-3 h-3 bg-purple-400/20 rounded-full"
            animate={{
              x: [0, 150, 0],
              y: [0, -120, 0],
              rotate: [0, 360, 0],
            }}
            transition={{
              duration: 12 + i * 3,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
            style={{
              left: `${5 + i * 12}%`,
              top: `${15 + i * 8}%`,
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
                animate={{ 
                  rotate: 360,
                  scale: [1, 1.1, 1]
                }}
                transition={{ 
                  rotate: { duration: 25, repeat: Infinity, ease: 'linear' },
                  scale: { duration: 4, repeat: Infinity, ease: 'easeInOut' }
                }}
                className="inline-block"
              >
                <div className="w-28 h-28 bg-gradient-to-r from-purple-500 to-blue-600 rounded-3xl flex items-center justify-center mb-6 shadow-2xl shadow-purple-500/30">
                  <UserPlus className="h-14 w-14 text-white" />
                </div>
              </motion.div>
            </div>

            <h1 className="text-6xl font-bold text-white mb-4 bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
              Katılın
            </h1>
            
            <p className="text-xl text-gray-300 mb-8 max-w-md">
              Geleceğin trading platformuna hoş geldiniz. Yapay zeka ile tanışın.
            </p>

            {/* Features */}
            <div className="space-y-6">
              {[
                { icon: Brain, text: 'AI destekli strateji geliştirme', color: 'text-purple-400' },
                { icon: Zap, text: 'Gerçek zamanlı piyasa analizi', color: 'text-blue-400' },
                { icon: Shield, text: 'Kurumsal düzey güvenlik', color: 'text-green-400' },
                { icon: TrendingUp, text: 'Profesyonel trading araçları', color: 'text-yellow-400' }
              ].map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + index * 0.1 }}
                  className="flex items-center text-gray-300"
                >
                  <feature.icon className={`h-6 w-6 ${feature.color} mr-4`} />
                  <span className="text-lg">{feature.text}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Right Side - Register Form */}
        <div className="w-full lg:w-1/2 flex items-center justify-center p-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="w-full max-w-md"
          >
            {/* Register Card */}
            <Card className="bg-black/40 border-gray-700 backdrop-blur-xl shadow-2xl">
              <CardContent className="p-8">
                <div className="text-center mb-8">
                  <h2 className="text-3xl font-bold text-white mb-2">
                    Hesap Oluşturun
                  </h2>
                  <p className="text-gray-400">
                    AI Algo Trade ailesine katılın
                  </p>
                </div>

                {/* Tab Navigation */}
                <div className="flex space-x-2 mb-8 bg-gray-800/30 p-2 rounded-xl">
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
                    {/* Email Registration */}
                    {activeTab === 'email' && (
                      <form onSubmit={handleEmailRegister} className="space-y-6">
                        <div className="space-y-2">
                          <label className="text-sm font-medium text-gray-300">
                            Ad Soyad (İsteğe bağlı)
                          </label>
                          <div className="relative">
                            <User className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                            <Input
                              type="text"
                              placeholder="Adınızı ve soyadınızı girin"
                              value={emailForm.fullName}
                              onChange={(e) => setEmailForm(prev => ({ ...prev, fullName: e.target.value }))}
                              className="pl-11 bg-gray-800/50 border-gray-600 text-white placeholder-gray-400 h-12 focus:border-purple-500 transition-colors"
                            />
                          </div>
                        </div>

                        <div className="space-y-2">
                          <label className="text-sm font-medium text-gray-300">
                            Email Adresi *
                          </label>
                          <div className="relative">
                            <Mail className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                            <Input
                              type="email"
                              placeholder="Email adresinizi girin"
                              value={emailForm.email}
                              onChange={(e) => setEmailForm(prev => ({ ...prev, email: e.target.value }))}
                              className="pl-11 bg-gray-800/50 border-gray-600 text-white placeholder-gray-400 h-12 focus:border-purple-500 transition-colors"
                              required
                            />
                          </div>
                        </div>

                        <div className="space-y-2">
                          <label className="text-sm font-medium text-gray-300">
                            Şifre *
                          </label>
                          <div className="relative">
                            <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                            <Input
                              type={showPassword ? "text" : "password"}
                              placeholder="Güçlü bir şifre oluşturun"
                              value={emailForm.password}
                              onChange={(e) => setEmailForm(prev => ({ ...prev, password: e.target.value }))}
                              className="pl-11 pr-11 bg-gray-800/50 border-gray-600 text-white placeholder-gray-400 h-12 focus:border-purple-500 transition-colors"
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
                          <p className="text-xs text-gray-500">
                            En az 8 karakter, büyük harf, küçük harf ve sayı içermeli
                          </p>
                        </div>

                        <div className="space-y-2">
                          <label className="text-sm font-medium text-gray-300">
                            Şifre Tekrarı *
                          </label>
                          <div className="relative">
                            <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                            <Input
                              type={showConfirmPassword ? "text" : "password"}
                              placeholder="Şifrenizi tekrar girin"
                              value={emailForm.confirmPassword}
                              onChange={(e) => setEmailForm(prev => ({ ...prev, confirmPassword: e.target.value }))}
                              className="pl-11 pr-11 bg-gray-800/50 border-gray-600 text-white placeholder-gray-400 h-12 focus:border-purple-500 transition-colors"
                              required
                            />
                            <button
                              type="button"
                              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                              className="absolute right-3 top-3 text-gray-400 hover:text-white transition-colors"
                            >
                              {showConfirmPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                            </button>
                          </div>
                        </div>

                        <Button
                          type="submit"
                          className="w-full h-12 bg-gradient-to-r from-purple-500 to-blue-600 hover:from-purple-600 hover:to-blue-700 text-white font-semibold rounded-xl transition-all duration-300 shadow-lg shadow-purple-500/25"
                          disabled={loading}
                        >
                          {loading ? (
                            <>
                              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                              Hesap oluşturuluyor...
                            </>
                          ) : (
                            <>
                              Hesap Oluştur
                              <ArrowRight className="ml-2 h-5 w-5" />
                            </>
                          )}
                        </Button>
                      </form>
                    )}

                    {/* Phone Registration */}
                    {activeTab === 'phone' && (
                      <form onSubmit={handlePhoneRegister} className="space-y-6">
                        <div className="space-y-2">
                          <label className="text-sm font-medium text-gray-300">
                            Ad Soyad (İsteğe bağlı)
                          </label>
                          <div className="relative">
                            <User className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                            <Input
                              type="text"
                              placeholder="Adınızı ve soyadınızı girin"
                              value={phoneForm.fullName}
                              onChange={(e) => setPhoneForm(prev => ({ ...prev, fullName: e.target.value }))}
                              className="pl-11 bg-gray-800/50 border-gray-600 text-white placeholder-gray-400 h-12 focus:border-purple-500 transition-colors"
                            />
                          </div>
                        </div>

                        <div className="space-y-2">
                          <label className="text-sm font-medium text-gray-300">
                            Telefon Numarası *
                          </label>
                          <div className="relative">
                            <Phone className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                            <Input
                              type="tel"
                              placeholder="+90 555 123 4567"
                              value={phoneForm.phone}
                              onChange={(e) => setPhoneForm(prev => ({ ...prev, phone: e.target.value }))}
                              className="pl-11 bg-gray-800/50 border-gray-600 text-white placeholder-gray-400 h-12 focus:border-purple-500 transition-colors"
                              required
                            />
                          </div>
                          <p className="text-xs text-gray-500">
                            Ülke kodunu dahil edin (örn: +90 Türkiye için)
                          </p>
                        </div>

                        <div className="space-y-2">
                          <label className="text-sm font-medium text-gray-300">
                            Şifre *
                          </label>
                          <div className="relative">
                            <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                            <Input
                              type={showPassword ? "text" : "password"}
                              placeholder="Güçlü bir şifre oluşturun"
                              value={phoneForm.password}
                              onChange={(e) => setPhoneForm(prev => ({ ...prev, password: e.target.value }))}
                              className="pl-11 pr-11 bg-gray-800/50 border-gray-600 text-white placeholder-gray-400 h-12 focus:border-purple-500 transition-colors"
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
                            Şifre Tekrarı *
                          </label>
                          <div className="relative">
                            <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                            <Input
                              type={showConfirmPassword ? "text" : "password"}
                              placeholder="Şifrenizi tekrar girin"
                              value={phoneForm.confirmPassword}
                              onChange={(e) => setPhoneForm(prev => ({ ...prev, confirmPassword: e.target.value }))}
                              className="pl-11 pr-11 bg-gray-800/50 border-gray-600 text-white placeholder-gray-400 h-12 focus:border-purple-500 transition-colors"
                              required
                            />
                            <button
                              type="button"
                              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                              className="absolute right-3 top-3 text-gray-400 hover:text-white transition-colors"
                            >
                              {showConfirmPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                            </button>
                          </div>
                        </div>

                        <div className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-xl p-3">
                          <p className="text-xs text-blue-400">
                            📱 Telefon numaranıza SMS doğrulama kodu gönderilecek
                          </p>
                        </div>

                        <Button
                          type="submit"
                          className="w-full h-12 bg-gradient-to-r from-purple-500 to-blue-600 hover:from-purple-600 hover:to-blue-700 text-white font-semibold rounded-xl transition-all duration-300 shadow-lg shadow-purple-500/25"
                          disabled={loading}
                        >
                          {loading ? (
                            <>
                              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                              Hesap oluşturuluyor...
                            </>
                          ) : (
                            <>
                              Hesap Oluştur
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
                  <div className="text-center text-sm text-gray-400">
                    Zaten hesabınız var mı?{' '}
                    <button
                      onClick={() => router.push('/auth/login')}
                      className="text-purple-400 hover:text-purple-300 font-medium transition-colors"
                    >
                      Buradan giriş yapın
                    </button>
                  </div>
                  
                  <div className="text-center text-xs text-gray-500">
                    Kayıt olarak{' '}
                    <span className="text-purple-400">Kullanım Şartları</span> ve{' '}
                    <span className="text-purple-400">Gizlilik Politikası</span>'nı kabul etmiş olursunuz.
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