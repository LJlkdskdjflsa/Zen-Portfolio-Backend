# Zen Portfolio Backend

**The AI-Driven DeBank Engine for Solana**

---

## Overview

Zen Portfolio Backend powers the AI-driven, cross-chain portfolio management experience for Zen Portfolio. It enables unified wallet and asset tracking, AI-powered yield/risk recommendations, and seamless portfolio optimization—bringing the best of EVM DeFi UX to Solana and beyond.

---

## Mission & Vision

**Mission:**  
Empower anyone—regardless of expertise—to confidently manage, optimize, and grow their digital assets on Solana and EVM chains through intelligent, actionable insights and seamless APIs.

**Vision:**  
Be the first AI-powered DeBank engine for Solana, lowering barriers and enabling users to invest with clarity, safety, and confidence.

---

## Problem Statement

- Fragmented wallet and asset management on Solana
- Poor yield discovery and idle tokens
- No unified risk alerts or optimization tools
- Lack of time/expertise for ongoing portfolio management

---

## Solution

Zen Portfolio Backend provides:

- **Unified, cross-chain API** (Solana + EVM)
- **AI-driven yield opportunity detection** and risk alerts
- **One-click optimization** (rebalance, migrate, bridge)
- **Multi-wallet management** and asset bridging
- **Personalized, actionable recommendations**

---

## Key Features

- Multi-wallet import (Solana, EVM, CeFi)
- Real-time portfolio analysis and asset breakdown
- AI-powered yield and risk recommendations (API endpoints)
- One-click optimization and bridging
- Modular FastAPI architecture for easy extension
- Technical analysis and risk alerts for assets
- News aggregation and alerts for user portfolio

---

## Architecture

- **Framework:** FastAPI (Python 3.13+)
- **Routers:** Modular endpoints for wallet, optimization, health, and swaps
- **Clients:** Integrations with Moralis, Helius, and more
- **Database:** Alembic/PostgreSQL for migrations and storage
- **AI Engine:** Langchain, OpenAI, and custom logic

---

## Current Project Status (as of 2025-05-17)

**Live Features:**
- Unified wallet import (Solana/EVM)
- AI-powered yield and risk recommendations (MVP)
- One-click portfolio optimization (MVP)
- Basic cross-chain bridge integration (Solana ⇄ EVM)
- Modular, extensible FastAPI codebase

**Limitations / In Progress:**
- AI engine is in MVP stage—recommendations are improving but not yet fully personalized
- Cross-chain bridging supports a limited set of assets/protocols
- Advanced analytics and visualizations are under development
- Mobile UI and push notifications are planned

---

## Roadmap

- [ ] Advanced AI-powered asset management (predictive, intent-driven)
- [ ] Personalized notifications and push-driven experience
- [ ] Frictionless onboarding from TradFi, CeFi, and EVM chains
- [ ] Deeper analytics and next-gen visualizations
- [ ] 24/7 DeFi AI concierge
- [ ] Expanded protocol and chain support

---

## Getting Started

### 1. Install Dependencies (Poetry)

```bash
poetry install --no-root
```

### 2. Configure Environment

Copy `.env.example` or `.env.local` and fill in required API keys (see below).

```env
OPENAI_KEY=your_openai_key
HELIUS_API_KEY=your_helius_key
# ... other keys as needed
```

### 3. Run Locally

```bash
poetry run uvicorn app.main:app --reload
```

### 4. Run with Docker (WIP)

```bash
docker-compose up -d
```

### 5. Database Setup

Ensure PostgreSQL is running. Then:

**Sync latest DB:**
```bash
IS_LOCAL=true alembic upgrade head
```

**Make migrations:** (Do NOT use --autogenerate)
```bash
poetry run alembic revision -m "Initial migration"
```

---

## API Endpoints (Key Examples)

- `GET /health` — Health check
- `GET /wallet/{wallet_address}/token-balances` — Get balances for Solana/EVM wallet
- `POST /optimization/solana` — Get optimization suggestions for Solana assets
- `POST /transactions/solana` — Get quote & swap transaction for Solana

> See FastAPI docs or `/app/routers/` for full endpoint list and schemas.

---

## Contributing

We welcome contributions! Please open issues or pull requests for features, bugfixes, or improvements.

---

## Contact

**Email:** liliagnjya@gmail.com  
**Join us in making Solana DeFi accessible, intelligent, and user-centric!**
