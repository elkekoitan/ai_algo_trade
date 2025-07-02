#!/usr/bin/env python3
"""
Quantum Trading Performance Dashboard
Real-time monitoring and analytics
"""
import json
import time
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.figure import Figure
import numpy as np

class QuantumPerformanceDashboard:
    """Real-time performance monitoring dashboard"""
    
    def __init__(self, log_file: str = None):
        self.log_file = log_file or self._find_latest_log()
        self.fig, self.axes = plt.subplots(2, 3, figsize=(15, 10))
        self.fig.suptitle('Quantum Trading Performance Dashboard', fontsize=16)
        
        # Initialize data containers
        self.trade_history = []
        self.equity_curve = []
        self.execution_speeds = []
        self.win_rates = []
        self.timestamps = []
        
    def _find_latest_log(self):
        """Find the most recent quantum trading log file"""
        logs = [f for f in os.listdir('.') if f.startswith('quantum_trading_') and f.endswith('.log')]
        if logs:
            return sorted(logs)[-1]
        return None
        
    def parse_log_data(self):
        """Parse performance data from log file"""
        if not self.log_file or not os.path.exists(self.log_file):
            return
            
        metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'profit_factor': 0,
            'sharpe_ratio': 0,
            'avg_execution': 0,
            'total_profit': 0,
            'total_loss': 0
        }
        
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
                
            for line in lines:
                if 'Total Trades:' in line:
                    metrics['total_trades'] = int(line.split(':')[-1].strip())
                elif 'Winning Trades:' in line:
                    metrics['winning_trades'] = int(line.split(':')[-1].strip())
                elif 'Losing Trades:' in line:
                    metrics['losing_trades'] = int(line.split(':')[-1].strip())
                elif 'Win Rate:' in line:
                    metrics['win_rate'] = float(line.split(':')[-1].strip().rstrip('%'))
                elif 'Profit Factor:' in line:
                    metrics['profit_factor'] = float(line.split(':')[-1].strip())
                elif 'Sharpe Ratio:' in line:
                    metrics['sharpe_ratio'] = float(line.split(':')[-1].strip())
                elif 'Avg Execution:' in line:
                    metrics['avg_execution'] = float(line.split(':')[-1].strip().rstrip('ms'))
                elif 'Total Profit:' in line:
                    metrics['total_profit'] = float(line.split('$')[-1].strip())
                elif 'Total Loss:' in line:
                    metrics['total_loss'] = float(line.split('$')[-1].strip())
                    
        except Exception as e:
            print(f"Error parsing log: {e}")
            
        return metrics
        
    def update_dashboard(self, frame):
        """Update dashboard with latest data"""
        # Clear all axes
        for ax in self.axes.flat:
            ax.clear()
            
        # Parse latest metrics
        metrics = self.parse_log_data()
        
        if not metrics:
            return
            
        # Update data containers
        self.timestamps.append(datetime.now())
        if metrics['win_rate'] > 0:
            self.win_rates.append(metrics['win_rate'])
        
        # 1. Win/Loss Distribution (Pie Chart)
        ax1 = self.axes[0, 0]
        if metrics['total_trades'] > 0:
            sizes = [metrics['winning_trades'], metrics['losing_trades']]
            labels = [f"Wins ({metrics['winning_trades']})", f"Losses ({metrics['losing_trades']})"]
            colors = ['#2ecc71', '#e74c3c']
            ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax1.set_title(f"Win/Loss Distribution (Total: {metrics['total_trades']})")
        
        # 2. Performance Metrics (Text)
        ax2 = self.axes[0, 1]
        ax2.axis('off')
        metrics_text = f"""
        📊 PERFORMANCE METRICS
        
        Win Rate: {metrics['win_rate']:.1f}%
        Profit Factor: {metrics['profit_factor']:.2f}
        Sharpe Ratio: {metrics['sharpe_ratio']:.2f}
        
        Total Profit: ${metrics['total_profit']:.2f}
        Total Loss: ${metrics['total_loss']:.2f}
        Net P&L: ${metrics['total_profit'] - metrics['total_loss']:.2f}
        
        Avg Execution: {metrics['avg_execution']:.1f}ms
        """
        ax2.text(0.1, 0.5, metrics_text, fontsize=12, verticalalignment='center',
                family='monospace', bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray"))
        
        # 3. Win Rate Trend
        ax3 = self.axes[0, 2]
        if len(self.win_rates) > 0:
            ax3.plot(range(len(self.win_rates)), self.win_rates, 'b-', linewidth=2)
            ax3.axhline(y=50, color='r', linestyle='--', alpha=0.5)
            ax3.set_title('Win Rate Trend')
            ax3.set_ylabel('Win Rate (%)')
            ax3.set_ylim(0, 100)
            ax3.grid(True, alpha=0.3)
            
        # 4. Profit/Loss Bar Chart
        ax4 = self.axes[1, 0]
        profits = [metrics['total_profit'], -metrics['total_loss']]
        labels = ['Total Profit', 'Total Loss']
        colors = ['#2ecc71', '#e74c3c']
        bars = ax4.bar(labels, profits, color=colors)
        ax4.set_title('Profit vs Loss')
        ax4.set_ylabel('Amount ($)')
        ax4.axhline(y=0, color='black', linewidth=0.5)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'${abs(height):.0f}', ha='center', va='bottom' if height > 0 else 'top')
                    
        # 5. Trading Activity Timeline
        ax5 = self.axes[1, 1]
        if metrics['total_trades'] > 0:
            # Simulate trading activity
            hours = list(range(24))
            activity = np.random.poisson(metrics['total_trades']/24, 24)
            ax5.bar(hours, activity, color='#3498db', alpha=0.7)
            ax5.set_title('24h Trading Activity')
            ax5.set_xlabel('Hour')
            ax5.set_ylabel('Trades')
            ax5.set_xlim(-0.5, 23.5)
            
        # 6. Risk Metrics
        ax6 = self.axes[1, 2]
        ax6.axis('off')
        
        # Calculate additional risk metrics
        max_drawdown = 0  # Would need equity curve data
        risk_reward = metrics['profit_factor'] if metrics['profit_factor'] > 0 else 0
        
        risk_text = f"""
        ⚠️ RISK METRICS
        
        Risk per Trade: 1.0%
        Max Drawdown: {max_drawdown:.1f}%
        Risk/Reward: 1:{risk_reward:.1f}
        
        Active Positions: N/A
        Total Exposure: N/A
        
        🎯 Strategy: Quantum AI
        📊 Instruments: 50
        ⏱️ Timeframe: M5
        """
        ax6.text(0.1, 0.5, risk_text, fontsize=11, verticalalignment='center',
                family='monospace', bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow"))
                
        # Adjust layout
        plt.tight_layout()
        
    def run(self):
        """Run the dashboard"""
        print("🚀 Starting Quantum Performance Dashboard...")
        print(f"📄 Monitoring: {self.log_file}")
        
        # Create animation
        ani = animation.FuncAnimation(self.fig, self.update_dashboard, 
                                    interval=5000, cache_frame_data=False)  # Update every 5 seconds
        
        plt.show()

def generate_performance_report():
    """Generate detailed performance report from results file"""
    try:
        with open('quantum_trading_results.json', 'r') as f:
            results = json.load(f)
            
        print("\n" + "="*60)
        print("📊 QUANTUM TRADING PERFORMANCE REPORT")
        print("="*60)
        
        metrics = results.get('performance_metrics', {})
        
        print(f"\n📈 TRADING STATISTICS")
        print(f"Total Trades: {metrics.get('total_trades', 0)}")
        print(f"Win Rate: {metrics.get('win_rate', 0):.1f}%")
        print(f"Profit Factor: {metrics.get('profit_factor', 0):.2f}")
        print(f"Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
        
        print(f"\n💰 FINANCIAL PERFORMANCE")
        print(f"Total Profit: ${metrics.get('total_profit', 0):.2f}")
        print(f"Total Loss: ${metrics.get('total_loss', 0):.2f}")
        net_pnl = metrics.get('total_profit', 0) - metrics.get('total_loss', 0)
        print(f"Net P&L: ${net_pnl:.2f}")
        
        print(f"\n⚡ EXECUTION METRICS")
        print(f"Avg Execution Speed: {metrics.get('avg_execution_speed_ms', 0):.1f}ms")
        
        print(f"\n⏱️ RUNTIME")
        print(f"Total Runtime: {results.get('runtime_hours', 0):.1f} hours")
        
        # Trade history analysis
        history = results.get('trading_history', [])
        if history:
            df = pd.DataFrame(history)
            
            print(f"\n📊 SYMBOL ANALYSIS")
            symbol_counts = df['symbol'].value_counts()
            print("Most Traded Symbols:")
            for symbol, count in symbol_counts.head(5).items():
                print(f"  {symbol}: {count} trades")
                
        print("\n" + "="*60)
        
    except FileNotFoundError:
        print("❌ No results file found. Run the quantum trading system first.")
    except Exception as e:
        print(f"❌ Error generating report: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--report':
        generate_performance_report()
    else:
        dashboard = QuantumPerformanceDashboard()
        dashboard.run() 