#!/usr/bin/env python3
"""
AI Algo Trade - GitHub CI/CD Setup Automation
Automated setup script for GitHub repository and CI/CD pipeline
"""

import os
import subprocess
import json
import yaml
from pathlib import Path
import sys

class GitHubCICDSetup:
    def __init__(self):
        self.project_root = Path.cwd()
        self.github_dir = self.project_root / ".github"
        self.workflows_dir = self.github_dir / "workflows"
        
    def create_directories(self):
        """Create necessary directories for GitHub Actions"""
        print("📁 Creating GitHub Actions directories...")
        
        directories = [
            ".github",
            ".github/workflows",
            ".github/ISSUE_TEMPLATE",
            ".github/PULL_REQUEST_TEMPLATE",
            "monitoring/prometheus",
            "monitoring/grafana/dashboards",
            "monitoring/grafana/datasources",
            "monitoring/fluentd/conf",
            "nginx"
        ]
        
        for directory in directories:
            (self.project_root / directory).mkdir(parents=True, exist_ok=True)
            print(f"  ✅ Created: {directory}")
    
    def create_workflow_files(self):
        """Create GitHub Actions workflow files"""
        print("\n🔧 Creating GitHub Actions workflows...")
        
        # Main CI/CD Pipeline
        ci_cd_workflow = {
            "name": "AI Algo Trade CI/CD Pipeline",
            "on": {
                "push": {"branches": ["main", "develop", "feature/*"]},
                "pull_request": {"branches": ["main", "develop"]}
            },
            "env": {
                "PYTHON_VERSION": "3.11",
                "NODE_VERSION": "18"
            },
            "jobs": {
                "backend-test": {
                    "name": "Backend Tests",
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"name": "Checkout code", "uses": "actions/checkout@v4"},
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v4",
                            "with": {"python-version": "${{ env.PYTHON_VERSION }}"}
                        },
                        {
                            "name": "Install dependencies",
                            "run": "pip install -r requirements.txt\npip install pytest pytest-cov black isort flake8"
                        },
                        {"name": "Run tests", "run": "cd backend && pytest tests/ -v --cov=."}
                    ]
                },
                "frontend-test": {
                    "name": "Frontend Tests",
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"name": "Checkout code", "uses": "actions/checkout@v4"},
                        {
                            "name": "Set up Node.js",
                            "uses": "actions/setup-node@v4",
                            "with": {
                                "node-version": "${{ env.NODE_VERSION }}",
                                "cache": "npm",
                                "cache-dependency-path": "frontend/package-lock.json"
                            }
                        },
                        {"name": "Install dependencies", "run": "cd frontend && npm ci"},
                        {"name": "Run tests", "run": "cd frontend && npm run test:ci"},
                        {"name": "Build", "run": "cd frontend && npm run build"}
                    ]
                },
                "security-scan": {
                    "name": "Security Scan",
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"name": "Checkout code", "uses": "actions/checkout@v4"},
                        {
                            "name": "Run Trivy vulnerability scanner",
                            "uses": "aquasecurity/trivy-action@master",
                            "with": {
                                "scan-type": "fs",
                                "scan-ref": ".",
                                "format": "sarif",
                                "output": "trivy-results.sarif"
                            }
                        }
                    ]
                }
            }
        }
        
        workflow_file = self.workflows_dir / "ci-cd.yml"
        with open(workflow_file, 'w') as f:
            yaml.dump(ci_cd_workflow, f, default_flow_style=False, sort_keys=False)
        print(f"  ✅ Created: {workflow_file}")
        
        # Release workflow
        release_workflow = {
            "name": "Release",
            "on": {
                "push": {"tags": ["v*"]}
            },
            "jobs": {
                "release": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"name": "Checkout", "uses": "actions/checkout@v4"},
                        {
                            "name": "Create Release",
                            "uses": "actions/create-release@v1",
                            "env": {"GITHUB_TOKEN": "${{ secrets.GITHUB_TOKEN }}"},
                            "with": {
                                "tag_name": "${{ github.ref }}",
                                "release_name": "Release ${{ github.ref }}",
                                "draft": False,
                                "prerelease": False
                            }
                        }
                    ]
                }
            }
        }
        
        release_file = self.workflows_dir / "release.yml"
        with open(release_file, 'w') as f:
            yaml.dump(release_workflow, f, default_flow_style=False, sort_keys=False)
        print(f"  ✅ Created: {release_file}")
    
    def create_github_templates(self):
        """Create GitHub issue and PR templates"""
        print("\n📝 Creating GitHub templates...")
        
        # Issue template
        issue_template = """---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
- OS: [e.g. Windows 10]
- Browser [e.g. chrome, safari]
- Version [e.g. 22]

**Additional context**
Add any other context about the problem here.
"""
        
        issue_file = self.github_dir / "ISSUE_TEMPLATE" / "bug_report.md"
        with open(issue_file, 'w') as f:
            f.write(issue_template)
        print(f"  ✅ Created: {issue_file}")
        
        # PR template
        pr_template = """## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added new tests for changes
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for hard-to-understand areas
- [ ] Documentation updated
- [ ] No new warnings introduced

## Related Issues
Closes #(issue number)
"""
        
        pr_file = self.github_dir / "PULL_REQUEST_TEMPLATE.md"
        with open(pr_file, 'w') as f:
            f.write(pr_template)
        print(f"  ✅ Created: {pr_file}")
    
    def create_monitoring_configs(self):
        """Create monitoring and observability configurations"""
        print("\n📊 Creating monitoring configurations...")
        
        # Prometheus config
        prometheus_config = {
            "global": {
                "scrape_interval": "15s",
                "evaluation_interval": "15s"
            },
            "scrape_configs": [
                {
                    "job_name": "ai-algo-trade-backend",
                    "static_configs": [{"targets": ["backend:8002"]}],
                    "metrics_path": "/metrics",
                    "scrape_interval": "30s"
                },
                {
                    "job_name": "ai-algo-trade-frontend", 
                    "static_configs": [{"targets": ["frontend:3000"]}],
                    "metrics_path": "/api/metrics",
                    "scrape_interval": "30s"
                }
            ]
        }
        
        prometheus_file = self.project_root / "monitoring" / "prometheus" / "prometheus.yml"
        with open(prometheus_file, 'w') as f:
            yaml.dump(prometheus_config, f, default_flow_style=False)
        print(f"  ✅ Created: {prometheus_file}")
        
        # Grafana datasource
        grafana_datasource = {
            "apiVersion": 1,
            "datasources": [
                {
                    "name": "Prometheus",
                    "type": "prometheus",
                    "url": "http://prometheus:9090",
                    "access": "proxy",
                    "isDefault": True
                }
            ]
        }
        
        datasource_file = self.project_root / "monitoring" / "grafana" / "datasources" / "prometheus.yml"
        with open(datasource_file, 'w') as f:
            yaml.dump(grafana_datasource, f, default_flow_style=False)
        print(f"  ✅ Created: {datasource_file}")
    
    def create_nginx_config(self):
        """Create Nginx reverse proxy configuration"""
        print("\n🌐 Creating Nginx configuration...")
        
        nginx_config = """
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8002;
    }
    
    upstream frontend {
        server frontend:3000;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        # Frontend routes
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Backend API routes
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # WebSocket support
        location /ws {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
        }
    }
}
"""
        
        nginx_file = self.project_root / "nginx" / "nginx.conf"
        with open(nginx_file, 'w') as f:
            f.write(nginx_config)
        print(f"  ✅ Created: {nginx_file}")
    
    def create_environment_files(self):
        """Create environment configuration files"""
        print("\n🔧 Creating environment files...")
        
        # Environment template
        env_template = """# AI Algo Trade - Environment Configuration

# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# MT5 Configuration
MT5_LOGIN=25201110
MT5_PASSWORD=your_mt5_password
MT5_SERVER=Tickmill-Demo

# Copy Trading Accounts
MT5_COPY_LOGIN_1=25216036
MT5_COPY_PASSWORD_1=your_copy_password_1
MT5_COPY_LOGIN_2=25216037
MT5_COPY_PASSWORD_2=your_copy_password_2

# AI Services
OPENAI_API_KEY=your_openai_api_key

# Security
JWT_SECRET=your_jwt_secret_key
ENCRYPTION_KEY=your_encryption_key

# Monitoring
GRAFANA_PASSWORD=admin
PROMETHEUS_RETENTION=30d

# Deployment
DOCKER_REGISTRY=your_docker_registry
AWS_REGION=us-east-1
"""
        
        env_file = self.project_root / ".env.template"
        with open(env_file, 'w') as f:
            f.write(env_template)
        print(f"  ✅ Created: {env_file}")
        
        # Staging environment
        staging_env = env_template.replace("ENVIRONMENT=development", "ENVIRONMENT=staging")
        staging_env = staging_env.replace("DEBUG=true", "DEBUG=false")
        
        staging_file = self.project_root / ".env.staging"
        with open(staging_file, 'w') as f:
            f.write(staging_env)
        print(f"  ✅ Created: {staging_file}")
        
        # Production environment
        prod_env = env_template.replace("ENVIRONMENT=development", "ENVIRONMENT=production")
        prod_env = prod_env.replace("DEBUG=true", "DEBUG=false")
        prod_env = prod_env.replace("LOG_LEVEL=INFO", "LOG_LEVEL=WARNING")
        
        prod_file = self.project_root / ".env.production"
        with open(prod_file, 'w') as f:
            f.write(prod_env)
        print(f"  ✅ Created: {prod_file}")
    
    def create_docker_files(self):
        """Create Docker configuration files"""
        print("\n🐳 Creating Docker configurations...")
        
        # Backend Dockerfile
        backend_dockerfile = """FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \\
    gcc g++ git curl build-essential && \\
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \\
    pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY *.py ./

RUN adduser --disabled-password --gecos '' appuser && \\
    chown -R appuser:appuser /app
USER appuser

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8002/health || exit 1

EXPOSE 8002

CMD ["python", "backend/simple_mt5_backend.py"]
"""
        
        backend_docker_file = self.project_root / "backend" / "Dockerfile"
        with open(backend_docker_file, 'w') as f:
            f.write(backend_dockerfile)
        print(f"  ✅ Created: {backend_docker_file}")
        
        # Frontend Dockerfile
        frontend_dockerfile = """FROM node:18-alpine AS base
RUN apk add --no-cache libc6-compat
WORKDIR /app

FROM base AS deps
COPY package.json package-lock.json* ./
RUN npm ci --only=production

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
"""
        
        frontend_docker_file = self.project_root / "frontend" / "Dockerfile"
        with open(frontend_docker_file, 'w') as f:
            f.write(frontend_dockerfile)
        print(f"  ✅ Created: {frontend_docker_file}")
    
    def setup_git_hooks(self):
        """Setup Git hooks for development"""
        print("\n🪝 Setting up Git hooks...")
        
        pre_commit_hook = """#!/bin/sh
# Pre-commit hook for AI Algo Trade

echo "🔍 Running pre-commit checks..."

# Backend checks
echo "📦 Checking backend code..."
cd backend
python -m black --check . || exit 1
python -m isort --check-only . || exit 1
python -m flake8 . || exit 1

# Frontend checks  
echo "🎨 Checking frontend code..."
cd ../frontend
npm run lint || exit 1
npm run type-check || exit 1

echo "✅ Pre-commit checks passed!"
"""
        
        hooks_dir = self.project_root / ".git" / "hooks"
        if hooks_dir.exists():
            hook_file = hooks_dir / "pre-commit"
            with open(hook_file, 'w') as f:
                f.write(pre_commit_hook)
            os.chmod(hook_file, 0o755)
            print(f"  ✅ Created: {hook_file}")
        else:
            print("  ⚠️  Git hooks directory not found. Initialize git first.")
    
    def create_scripts(self):
        """Create utility scripts"""
        print("\n📜 Creating utility scripts...")
        
        # Development setup script
        setup_script = """#!/bin/bash
# AI Algo Trade - Development Setup

echo "🚀 Setting up AI Algo Trade development environment..."

# Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "Python 3.11+ required"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Node.js 18+ required"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "Docker required"; exit 1; }

# Backend setup
echo "📦 Setting up backend..."
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend setup
echo "🎨 Setting up frontend..."
cd ../frontend
npm install

echo "✅ Development environment ready!"
echo "Run 'npm run dev' to start development"
"""
        
        setup_file = self.project_root / "scripts" / "setup-dev.sh"
        setup_file.parent.mkdir(exist_ok=True)
        with open(setup_file, 'w') as f:
            f.write(setup_script)
        os.chmod(setup_file, 0o755)
        print(f"  ✅ Created: {setup_file}")
        
        # Deployment script
        deploy_script = """#!/bin/bash
# AI Algo Trade - Deployment Script

ENVIRONMENT=${1:-staging}

echo "🚀 Deploying to $ENVIRONMENT..."

# Build and push images
docker-compose build
docker tag ai-algo-trade_backend:latest $DOCKER_REGISTRY/ai-algo-trade-backend:$ENVIRONMENT
docker tag ai-algo-trade_frontend:latest $DOCKER_REGISTRY/ai-algo-trade-frontend:$ENVIRONMENT

docker push $DOCKER_REGISTRY/ai-algo-trade-backend:$ENVIRONMENT
docker push $DOCKER_REGISTRY/ai-algo-trade-frontend:$ENVIRONMENT

echo "✅ Deployment to $ENVIRONMENT completed!"
"""
        
        deploy_file = self.project_root / "scripts" / "deploy.sh"
        with open(deploy_file, 'w') as f:
            f.write(deploy_script)
        os.chmod(deploy_file, 0o755)
        print(f"  ✅ Created: {deploy_file}")
    
    def run_setup(self):
        """Run the complete setup process"""
        print("🎯 AI Algo Trade - GitHub CI/CD Setup")
        print("=" * 50)
        
        try:
            self.create_directories()
            self.create_workflow_files()
            self.create_github_templates()
            self.create_monitoring_configs()
            self.create_nginx_config()
            self.create_environment_files()
            self.create_docker_files()
            self.setup_git_hooks()
            self.create_scripts()
            
            print("\n🎉 GitHub CI/CD setup completed successfully!")
            print("\nNext steps:")
            print("1. Create GitHub repository")
            print("2. Add secrets to repository settings")
            print("3. Push code to GitHub")
            print("4. Configure branch protection rules")
            print("5. Start parallel development!")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Setup failed: {e}")
            return False

def main():
    """Main function"""
    setup = GitHubCICDSetup()
    success = setup.run_setup()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 