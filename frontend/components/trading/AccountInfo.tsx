'use client'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { DollarSign, TrendingUp, BarChart, ShieldCheck, Loader2 } from "lucide-react"
import { AccountInfo as AccountInfoType } from '@/lib/types'

interface AccountInfoProps {
  account: AccountInfoType | null
  isLoading: boolean
}

export default function AccountInfo({ account, isLoading }: AccountInfoProps) {

  if (isLoading) {
    return (
      <Card className="bg-gray-900/50 border-gray-800 text-white">
        <CardHeader>
          <CardTitle>Account Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex justify-center items-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-cyan-400"/>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!account) {
    return (
      <Card className="bg-gray-900/50 border-gray-800 text-white">
        <CardHeader>
          <CardTitle>Account Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">No account data available.</div>
        </CardContent>
      </Card>
    )
  }

  const profitColor = account.profit >= 0 ? 'text-green-400' : 'text-red-400';

  return (
    <Card className="bg-gray-900/50 border-gray-800 text-white">
      <CardHeader>
        <CardTitle>Account Information</CardTitle>
        <p className="text-sm text-gray-400">
            Account #{account.login} ({account.server})
        </p>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-center">
          <div>
            <p className="text-sm text-gray-400">Balance</p>
            <p className="text-2xl font-bold text-blue-400 flex items-center justify-center">
              <DollarSign className="h-5 w-5 mr-1"/> 
              {account.balance?.toLocaleString()}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-400">Equity</p>
            <p className="text-2xl font-bold text-purple-400 flex items-center justify-center">
                <BarChart className="h-5 w-5 mr-1"/>
                {account.equity?.toLocaleString()}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-400">Floating P/L</p>
            <p className={`text-2xl font-bold ${profitColor} flex items-center justify-center`}>
                <TrendingUp className="h-5 w-5 mr-1"/>
                {account.profit?.toLocaleString()}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-400">Leverage</p>
            <p className="text-2xl font-bold text-yellow-400 flex items-center justify-center">
                <ShieldCheck className="h-5 w-5 mr-1"/>
                1:{account.leverage}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
} 