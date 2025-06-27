import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import QuantumLayout from '@/components/layout/QuantumLayout'
import { AppProvider } from '@/lib/context'
import { TranslationsProvider } from '@/lib/translations/context'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AI Algo Trade - Quantum Edition',
  description: 'Advanced AI-powered algorithmic trading platform with real-time MT5 integration and ICT analysis.',
}

export const viewport: Viewport = {
  themeColor: '#0a0a0f',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-quantum-dark text-gray-300`}>
        <TranslationsProvider>
          <AppProvider>
            <QuantumLayout>
              {children}
            </QuantumLayout>
          </AppProvider>
        </TranslationsProvider>
      </body>
    </html>
  )
}
