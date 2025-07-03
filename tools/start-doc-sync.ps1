# AI Algo Trade - Documentation Sync System Launcher
# This script sets up and runs the automatic documentation synchronization

param(
    [string]$Command = "start",
    [switch]$Background,
    [switch]$Install
)

# Color output functions
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Success { Write-ColorOutput Green @args }
function Write-Warning { Write-ColorOutput Yellow @args }
function Write-Error { Write-ColorOutput Red @args }
function Write-Info { Write-ColorOutput Cyan @args }

Write-Info "🚀 AI Algo Trade Documentation Sync System"
Write-Info "==========================================`n"

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✅ Node.js detected: $nodeVersion"
    } else {
        throw "Node.js not found"
    }
} catch {
    Write-Error "❌ Node.js is required but not installed."
    Write-Info "Please install Node.js from https://nodejs.org/"
    exit 1
}

# Install dependencies if requested
if ($Install) {
    Write-Info "📦 Installing dependencies..."
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ Failed to install dependencies"
        exit 1
    }
    Write-Success "✅ Dependencies installed successfully"
}

# Check if doc-sync-system.js exists
if (-not (Test-Path "doc-sync-system.js")) {
    Write-Error "❌ doc-sync-system.js not found in current directory"
    Write-Info "Please make sure you're running this script from the project root"
    exit 1
}

# Initialize configuration if it doesn't exist
if (-not (Test-Path ".doc-sync-config.json")) {
    Write-Info "🔧 Initializing documentation sync configuration..."
    node doc-sync-system.js init
    
    Write-Info "`n📝 Configuration created. Key settings:"
    Write-Info "   - Watch directories: src, components, modules, api, etc."
    Write-Info "   - File types: .js, .ts, .jsx, .tsx, .py, .php, etc."
    Write-Info "   - Sync interval: 30 seconds"
    Write-Info "   - Auto-commit to Git: enabled"
    Write-Info "`n✏️  Edit .doc-sync-config.json to customize these settings"
}

# Execute the requested command
switch ($Command.ToLower()) {
    "start" {
        Write-Info "🔄 Starting documentation sync system..."
        Write-Info "This will monitor your code files and automatically update documentation."
        Write-Info "Press Ctrl+C to stop.`n"
        
        if ($Background) {
            Write-Info "🌙 Running in background mode..."
            Start-Process -WindowStyle Hidden node -ArgumentList "doc-sync-system.js", "start"
            Write-Success "✅ Documentation sync started in background"
        } else {
            node doc-sync-system.js start
        }
    }
    
    "sync" {
        Write-Info "🔄 Performing one-time documentation sync..."
        node doc-sync-system.js sync
        Write-Success "✅ Documentation sync completed"
    }
    
    "stop" {
        Write-Info "🛑 Stopping documentation sync processes..."
        Get-Process -Name "node" -ErrorAction SilentlyContinue | 
            Where-Object { $_.CommandLine -like "*doc-sync-system*" } | 
            Stop-Process -Force
        Write-Success "✅ Documentation sync stopped"
    }
    
    "status" {
        Write-Info "📊 Checking documentation sync status..."
        
        if (Test-Path ".doc-sync-state.json") {
            $state = Get-Content ".doc-sync-state.json" | ConvertFrom-Json
            if ($state.lastSync) {
                Write-Success "✅ Last sync: $($state.lastSync)"
                Write-Info "📁 Monitored files: $($state.fileHashes.Count)"
            } else {
                Write-Warning "⚠️  No sync performed yet"
            }
        } else {
            Write-Warning "⚠️  Documentation sync not initialized"
        }
        
        # Check for running processes
        $runningProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue | 
            Where-Object { $_.CommandLine -like "*doc-sync-system*" }
        
        if ($runningProcesses) {
            Write-Success "✅ Documentation sync is running (PID: $($runningProcesses.Id -join ', '))"
        } else {
            Write-Warning "⚠️  Documentation sync is not running"
        }
    }
    
    "health" {
        Write-Info "🏥 Running documentation health check..."
        if (Test-Path "doc-health-scanner.js") {
            node doc-health-scanner.js
        } else {
            Write-Warning "⚠️  doc-health-scanner.js not found"
        }
    }
    
    "config" {
        Write-Info "⚙️  Opening configuration file..."
        if (Test-Path ".doc-sync-config.json") {
            if (Get-Command "code" -ErrorAction SilentlyContinue) {
                code .doc-sync-config.json
            } else {
                notepad .doc-sync-config.json
            }
        } else {
            Write-Warning "⚠️  Configuration file not found. Run with 'start' command first."
        }
    }
    
    "help" {
        Write-Info @"
📚 Documentation Sync System Commands:

  start       Start the documentation sync daemon
  sync        Perform a one-time documentation sync
  stop        Stop all documentation sync processes
  status      Check the current sync status
  health      Run documentation health check
  config      Open configuration file for editing
  help        Show this help message

Options:
  -Background  Run in background (for 'start' command)
  -Install     Install Node.js dependencies first

Examples:
  .\start-doc-sync.ps1 start
  .\start-doc-sync.ps1 start -Background
  .\start-doc-sync.ps1 sync
  .\start-doc-sync.ps1 status

Integration with Cursor IDE:
1. Add this script to your VS Code/Cursor tasks.json:
   {
     "label": "Start Doc Sync",
     "type": "shell",
     "command": "powershell",
     "args": ["-File", "start-doc-sync.ps1", "start", "-Background"],
     "group": "build"
   }

2. Set up a keyboard shortcut for quick sync:
   {
     "key": "ctrl+shift+d",
     "command": "workbench.action.terminal.sendSequence",
     "args": { "text": ".\start-doc-sync.ps1 sync\n" }
   }
"@
    }
    
    default {
        Write-Warning "❓ Unknown command: $Command"
        Write-Info "Use 'help' command to see available options"
        exit 1
    }
}

# Show next steps if this is the first run
if ($Command -eq "start" -and -not (Test-Path ".doc-sync-state.json")) {
    Write-Info "`n📋 Next Steps:"
    Write-Info "1. The sync system is now monitoring your code files"
    Write-Info "2. Make changes to any .js, .ts, .jsx, .tsx files in watched directories"
    Write-Info "3. Documentation will be automatically updated within 30 seconds"
    Write-Info "4. Check the 'docs/' folder for generated documentation"
    Write-Info "5. Use '.\start-doc-sync.ps1 status' to check sync status"
}
