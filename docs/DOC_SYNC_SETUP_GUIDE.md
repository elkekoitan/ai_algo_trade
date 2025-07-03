# 📚 Automatic Documentation Synchronization Setup Guide

## 🎯 Problem Solved

This system solves the common problem of **outdated documentation** by automatically:
- ✅ Detecting code changes in real-time
- ✅ Extracting API endpoints, functions, and components
- ✅ Updating documentation files automatically
- ✅ Checking documentation health and quality
- ✅ Integrating with Git for automatic commits
- ✅ Working seamlessly with Cursor IDE

## 🚀 Quick Start

### 1. Initialize the System
```powershell
# Run this once to set up everything
.\start-doc-sync.ps1 start
```

### 2. Start Using in Cursor IDE
- Press **Ctrl+Alt+D** to start documentation sync in background
- Press **Ctrl+Shift+D** to sync documentation immediately
- Press **Ctrl+Shift+H** to run documentation health check

### 3. Make Code Changes
The system automatically detects changes in:
- `/src/` - Source code files
- `/components/` - React components
- `/modules/` - Application modules
- `/api/` - API endpoints
- `/services/` - Service layers

## 📋 Features Overview

### 🔄 Automatic Documentation Generation
- **API Documentation**: Extracts endpoints, parameters, responses
- **Module Documentation**: Functions, classes, exports
- **Component Documentation**: React props, usage examples
- **README Updates**: Timestamps and change tracking

### 🏥 Documentation Health Monitoring
- **Link Checking**: Detects 404s and dead references
- **Markdown Linting**: Style, hierarchy, alt text validation
- **Quality Reports**: CSV exports with issues and severity

### 🔧 Smart Integration
- **File Watching**: Monitors specified directories automatically
- **Git Integration**: Auto-commits documentation changes
- **IDE Integration**: Tasks and keyboard shortcuts for Cursor
- **Configurable**: Customizable rules and patterns

## ⚙️ Configuration

### Default Configuration (`.doc-sync-config.json`)
```json
{
  "watchDirs": ["src", "components", "modules", "api", "services"],
  "watchExtensions": [".js", ".ts", ".jsx", ".tsx", ".py"],
  "syncInterval": 30000,
  "gitIntegration": {
    "enabled": true,
    "autoCommit": true
  }
}
```

### Customization Options
Edit `.doc-sync-config.json` to:
- Add/remove watched directories
- Change file extensions to monitor
- Adjust sync frequency
- Configure Git integration
- Set output file locations

## 🎮 Available Commands

### PowerShell Commands
```powershell
# Start documentation sync daemon
.\start-doc-sync.ps1 start

# Run in background (recommended for development)
.\start-doc-sync.ps1 start -Background

# Perform one-time sync
.\start-doc-sync.ps1 sync

# Check system status
.\start-doc-sync.ps1 status

# Run documentation health check
.\start-doc-sync.ps1 health

# Stop all sync processes
.\start-doc-sync.ps1 stop

# Open configuration file
.\start-doc-sync.ps1 config
```

### Cursor IDE Integration

#### Tasks (Ctrl+Shift+P → "Tasks: Run Task")
- 🚀 Start Documentation Sync
- 🔄 Sync Documentation Now
- 📊 Check Documentation Status
- 🏥 Run Documentation Health Check
- 🛑 Stop Documentation Sync
- ⚙️ Open Documentation Config

#### Keyboard Shortcuts
- **Ctrl+Alt+D**: Start sync in background
- **Ctrl+Shift+D**: Sync now
- **Ctrl+Shift+Alt+D**: Check status
- **Ctrl+Shift+H**: Health check

## 📁 Generated Documentation Structure

```
docs/
├── API_REFERENCE.md     # Auto-generated API endpoints
├── MODULES.md           # Module documentation
├── COMPONENTS.md        # React component docs
└── health/
    ├── doc-health-raw.csv      # Health check results
    └── doc-health-summary.txt  # Health summary
```

## 🔍 How It Works

### 1. File Monitoring
- Scans configured directories every 30 seconds
- Calculates MD5 hashes to detect changes
- Triggers documentation updates on modifications

### 2. Code Analysis
- **JavaScript/TypeScript**: Functions, classes, exports
- **React Components**: Props, interfaces, JSX
- **API Routes**: Express.js endpoints, parameters
- **Comments**: JSDoc extraction for descriptions

### 3. Documentation Generation
- Updates existing sections or creates new ones
- Preserves manual documentation
- Adds timestamps and file references
- Maintains proper Markdown formatting

### 4. Quality Assurance
- Link validation (local and external)
- Markdown style checking
- Image reference validation
- Heading hierarchy validation

## 🛠️ Troubleshooting

### Common Issues

#### "Node.js not found"
```powershell
# Install Node.js from https://nodejs.org/
# Or use winget:
winget install OpenJS.NodeJS
```

#### "doc-sync-system.js not found"
```powershell
# Make sure you're in the project root directory
cd C:\Users\elkek\Desktop\ai_algo_trade
```

#### Sync not detecting changes
```powershell
# Check if directories exist and are configured
.\start-doc-sync.ps1 config

# Verify file extensions are included
# Default: .js, .ts, .jsx, .tsx, .py
```

#### Git integration issues
```powershell
# Ensure Git is installed and repository is initialized
git --version
git status
```

### Debug Mode
```powershell
# Run with detailed logging
node doc-sync-system.js sync
```

## 📊 Health Check Results

The health scanner generates:

### CSV Report (`doc-health-raw.csv`)
```csv
file,line,issue,severity
"README.md","15","Line too long (150 characters)","info"
"docs/API.md","23","Dead local link: ./missing-file.md","error"
```

### Summary Report (`doc-health-summary.txt`)
- Total files scanned
- Issues by severity (error/warning/info)
- Health score percentage
- Top issue types

## 🎯 Best Practices

### 1. Code Documentation
```javascript
/**
 * Calculates trading signals based on market data
 * @param {Object} marketData - Real-time market information
 * @returns {Object} Trading signals and recommendations
 */
function calculateTradingSignals(marketData) {
    // Implementation
}
```

### 2. React Component Documentation
```typescript
interface TradingDashboardProps {
    /** Current market data */
    marketData: MarketData;
    /** User trading preferences */
    preferences: UserPreferences;
    /** Callback when trade is executed */
    onTradeExecuted?: (trade: Trade) => void;
}
```

### 3. API Endpoint Documentation
```javascript
/**
 * Get user trading history
 * Returns paginated list of user trades
 */
router.get('/api/trades/:userId', async (req, res) => {
    // Implementation
    res.json({ trades: [], pagination: {} });
});
```

## 🔧 Advanced Configuration

### Custom Documentation Templates
Create custom templates in `.doc-sync-config.json`:

```json
{
  "templates": {
    "api": "# {{title}}\n\n**Endpoint**: {{method}} {{path}}\n\n{{description}}",
    "module": "## {{name}}\n\n{{description}}\n\n### Functions\n{{functions}}"
  }
}
```

### Selective Monitoring
```json
{
  "watchDirs": ["src/trading", "src/analysis"],
  "ignorePatterns": ["**/test/**", "**/*.spec.js"],
  "autoGenRules": {
    "api": {
      "enabled": true,
      "patterns": ["**/api/trading/**/*.js"]
    }
  }
}
```

## 🚀 Getting Started Checklist

- [ ] Clone/download the documentation sync system files
- [ ] Run `.\start-doc-sync.ps1 start` to initialize
- [ ] Configure watched directories in `.doc-sync-config.json`
- [ ] Add keyboard shortcuts to Cursor IDE
- [ ] Make a test code change to verify sync works
- [ ] Run health check: `.\start-doc-sync.ps1 health`
- [ ] Set up background sync: `.\start-doc-sync.ps1 start -Background`

## 💡 Tips for Maximum Effectiveness

1. **Use JSDoc comments** for better auto-generated descriptions
2. **Keep consistent naming** for modules and components
3. **Run health checks regularly** to maintain documentation quality
4. **Review auto-generated docs** and add manual context where needed
5. **Use descriptive commit messages** for documentation changes

## 🔗 Integration Examples

### Package.json Scripts
```json
{
  "scripts": {
    "docs:sync": "node doc-sync-system.js sync",
    "docs:health": "node doc-health-scanner.js",
    "docs:start": "node doc-sync-system.js start"
  }
}
```

### Git Hooks (Optional)
```bash
# .git/hooks/pre-commit
#!/bin/sh
node doc-sync-system.js sync
```

---

## 🎉 You're All Set!

Your documentation will now automatically stay synchronized with your code changes. The system runs in the background and intelligently updates documentation as you develop.

**Happy coding with always-fresh documentation! 📚✨**
