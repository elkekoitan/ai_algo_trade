import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';

// Initialize the Inter font
const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
});

// Metadata for the application
export const metadata: Metadata = {
  title: 'ICT Ultra v2: Algo Forge Edition',
  description: 'Next-generation algorithmic trading platform with MQL5 Algo Forge integration',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable}`}>
      <body className="bg-background min-h-screen">
        {children}
      </body>
    </html>
  );
} 