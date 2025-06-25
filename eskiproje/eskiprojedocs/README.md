# ICT Ultra Platform – Documentation Index

Welcome to the **ICT Ultra Platform** documentation hub. This project is a modular-monolith trading platform integrating directly with **MetaTrader&nbsp;5** (MT5) and providing institutional-grade tooling for signal generation, risk management, AI-based prediction, and fully automated trade execution.

> **Target audience**: algorithmic traders, quantitative researchers, backend/frontend engineers, DevOps engineers, and project contributors.

---

## 📚 Document Map

| Category | Document | Description |
|----------|----------|-------------|
| **Project Overview** | [`PROJECT_STATUS_2025.md`](../backend/docs/PROJECT_STATUS_2025.md) | High-level progress report and KPI metrics for the 2025 roadmap. |
| | [`PROJECT_STATUS_OVERVIEW.md`](../ICT_Ultra_Platform/docs/PROJECT_STATUS_OVERVIEW.md) | Condensed status summary across all services. |
| **Architecture** | [`ARCHITECTURE.md`](../backend/docs/ARCHITECTURE.md) | Component and data-flow diagrams for the modular-monolith backend. |
| | [`TECHNICAL_ARCHITECTURE_2025.md`](../ICT_Ultra_Platform/docs/TECHNICAL_ARCHITECTURE_2025.md) | Layered technical deep-dive including deployment topology. |
| | [`MODULAR_MONOLITH_ARCHITECTURE.md`](../backend/docs/MODULAR_MONOLITH_ARCHITECTURE.md) | Rationale behind the modular-monolith approach and DDD structure. |
| **Setup & Deployment** | [`SETUP_GUIDE.md`](SETUP_GUIDE.md) | Local development setup, environment variables, and first-run instructions. |
| | [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md) | Production deployment, Docker, CI/CD pipeline configuration. |
| | [`start_platform.bat`](../start-platform.bat) | One-click startup script for Windows environments. |
| **Integration Guides** | [`MT5_INTEGRATION_GUIDE.md`](MT5_INTEGRATION_GUIDE.md) | Step-by-step guide to connect the platform with MT5 using demo account **25201110**. |
| | [`SUPABASE_SETUP.md`](../ICT_Ultra_Platform/docs/SUPABASE_SETUP.md) | Instructions to enable optional Supabase analytics stack. |
| **Domain & Algorithms** | [`ALGORITHMS_OVERVIEW.md`](../backend/docs/ALGORITHMS_OVERVIEW.md) | Overview of trading, risk, and ML algorithms implemented. |
| | [`AI_ML_FEATURES_2025.md`](../backend/docs/AI_ML_FEATURES_2025.md) | Current and planned AI/ML functionality. |
| | [`COMPREHENSIVE_ICT_ROADMAP_2025.md`](../ICT_Ultra_Platform/docs/COMPREHENSIVE_ICT_ROADMAP_2025.md) | Detailed roadmap for ICT signal engine enhancements. |
| **Frontend & UX** | [`UI_UX_IMPROVEMENTS_2025.md`](../ICT_Ultra_Platform/docs/UI_UX_IMPROVEMENTS_2025.md) | UI/UX improvements roadmap with design references. |
| | [`UI_UX_DESIGN_ROADMAP_V2.md`](../ICT_Ultra_Platform/docs/UI_UX_DESIGN_ROADMAP_V2.md) | Full design system guidelines and component library specs. |
| **Developer Guides** | [`DEV_GUIDE.md`](../backend/docs/DEV_GUIDE.md) | Coding conventions, testing strategy, and pull-request workflow. |
| | [`DEVELOPMENT_GUIDE.md`](DEVELOPMENT_GUIDE.md) | Hands-on tutorials for extending modules & contributing. |
| | [`CONTRIBUTING.md`](CONTRIBUTING.md) | How to report issues and submit patches. |
| **Testing & QA** | [`TESTING_GUIDE.md`](TESTING_GUIDE.md) | End-to-end, integration, and unit testing instructions. |
| **Roadmap & Planning** | [`FEATURES_AND_ROADMAP_2025.md`](../ICT_Ultra_Platform/docs/FEATURES_AND_ROADMAP_2025.md) | Quarterly feature delivery schedule. |
| | [`NEXT_STEPS_AND_RECOMMENDATIONS_2025.md`](../NEXT_STEPS_AND_RECOMMENDATIONS_2025.md) | Immediate actionable tasks and future recommendations. |
| **Security & Compliance** | [`SECURITY_GUIDE.md`](SECURITY_GUIDE.md) | Platform security model, secrets management, and compliance notes. |
| **Knowledge Base** | [`KNOWLEDGE_BASE.md`](KNOWLEDGE_BASE.md) | Frequently asked questions and accumulated tribal knowledge. |

---

## 🔰 Quick Start

1. Clone the repository and install dependencies:
   ```bash
   git clone https://github.com/your-org/ict-ultra-platform.git
   cd ict-ultra-platform
   pnpm i  # installs Node workspaces & Python virtualenv via husky hook
   ```
2. Configure environment variables by copying `.env.example` files at project root and in `ICT_Ultra_Platform/`.
3. Follow [`SETUP_GUIDE.md`](SETUP_GUIDE.md) to launch backend (FastAPI), proxy (Node/Express), and frontend (Next.js).
4. Open `http://localhost:3000` to access the **Premium Dashboard**.

---

## 🧩 Folder Structure (High Level)

```
backend/                 # Python services & trading engine
ICT_Ultra_Platform/      # Node workspace (proxy, frontend, websocket)
└── apps/web/            # Next.js dashboard
└── scripts/             # Startup & recovery scripts
scripts/                 # Root-level helper scripts
services/                # Stand-alone micro-services (gateway, mt5_service)
```  

Refer to [`ARCHITECTURE.md`](../backend/docs/ARCHITECTURE.md) for the full component diagram.

---

## 🔎 Searching the Docs

Use your editor's global search or run:
```bash
rg "# .*" docs backend/docs ICT_Ultra_Platform/docs | less
```

---

### Maintaining Documentation

• Update the corresponding markdown whenever a feature is merged.  
• Keep diagrams in SVG/ASCII for version control friendliness.  
• Run `npm run docs:lint` (lints Markdown links & spelling) before opening a pull request.

---

For any missing topic, please create an issue or submit a PR to keep our knowledge base **ever-green**. 