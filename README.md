# PlacementPilot AI 🎓

> **AI-Powered Campus Placement Preparation Platform**  
> Built with **Python Flask** · **IBM watsonx.ai** · **IBM Granite Models** · **Bootstrap 5**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Quick Start (Local)](#quick-start-local)
- [IBM watsonx.ai Configuration](#ibm-watsonxai-configuration)
- [Customizing the AI Agent](#customizing-the-ai-agent)
- [Module Reference](#module-reference)
- [Deployment on IBM Cloud](#deployment-on-ibm-cloud)
- [Environment Variables](#environment-variables)
- [Tech Stack](#tech-stack)

---

## Overview

**PlacementPilot AI** is a full-stack intelligent placement preparation platform powered by **IBM Granite** language models through **IBM watsonx.ai**. It provides personalized, profile-aware guidance across every dimension of campus placement — from DSA roadmaps and resume analysis to mock interviews and company-specific strategies.

---

## Features

| Module | Description |
|--------|-------------|
| 🎯 **Student Profile Management** | Multi-profile support with branch, year, skill level, target companies |
| 📊 **Placement Dashboard** | Readiness score, radar chart, progress bars, strengths & weaknesses |
| 🗺️ **Personalized Roadmap** | AI week-by-week plan based on profile and timeline |
| 📄 **Resume Analyzer** | ATS score, action verbs, quantification tips, improvement suggestions |
| ❓ **Mock Interview** | Technical, System Design, HR, Aptitude rounds with ideal answers |
| 🧮 **Aptitude Practice** | Quantitative, logical, verbal questions with step-by-step solutions |
| 🏢 **Company Guide** | Company-specific interview strategies for 10+ major companies |
| 💻 **Project Ideas** | Curated project recommendations with tech stack and resume impact |
| 🏆 **Certifications** | Recommended certs (IBM, AWS, Google, Microsoft) by career goal |
| 🌐 **AI Chat** | 24/7 context-aware chat with IBM Granite across all modules |
| 👤 **HR Preparation** | STAR framework stories, behavioral questions, culture fit tips |
| 📈 **Progress Tracking** | Track completion across all 8 preparation areas |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Browser (Bootstrap 5 + JavaScript)                 │
│  ├── Dashboard (Chart.js)                           │
│  ├── Chat Interface                                 │
│  └── Module Pages                                   │
└────────────────────┬────────────────────────────────┘
                     │ HTTP / REST
┌────────────────────▼────────────────────────────────┐
│  Flask Backend (Python)                             │
│  ├── app.py              — Routes & session mgmt   │
│  ├── agent_instructions.py — AI behavior config    │
│  └── modules/                                       │
│       ├── ai_service.py  — IBM watsonx.ai calls    │
│       ├── profile_manager.py — JSON profile store  │
│       └── dashboard.py   — Stats engine            │
└────────────────────┬────────────────────────────────┘
                     │ ibm-watsonx-ai SDK
┌────────────────────▼────────────────────────────────┐
│  IBM watsonx.ai Platform                            │
│  └── IBM Granite 3.3 8B Instruct Model             │
└─────────────────────────────────────────────────────┘
```

---

## Project Structure

```
PlacementPilot/
├── app.py                        # Flask application entry point
├── agent_instructions.py         # ⭐ AI agent customization hub
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variable template
├── .env                          # Your local secrets (never commit!)
├── Procfile                      # For IBM Cloud / Heroku deployment
│
├── modules/
│   ├── __init__.py
│   ├── ai_service.py             # IBM watsonx.ai / Granite integration
│   ├── profile_manager.py        # Student profile CRUD (JSON files)
│   └── dashboard.py              # Placement readiness calculator
│
├── templates/
│   ├── base.html                 # Shared navbar, footer, dark mode
│   ├── index.html                # Landing page
│   ├── setup.html                # Profile creation / management
│   ├── dashboard.html            # Progress dashboard with charts
│   ├── chat.html                 # AI Chat interface
│   ├── roadmap.html              # Placement roadmap planner
│   ├── resume.html               # Resume analyzer
│   ├── interview.html            # Mock interview simulator
│   ├── aptitude.html             # Aptitude practice
│   ├── company_guide.html        # Company preparation guide
│   ├── projects.html             # Project recommendation engine
│   └── error.html                # 404/500 error pages
│
├── static/
│   ├── css/
│   │   └── style.css             # Custom CSS + dark mode + responsive
│   └── js/
│       ├── main.js               # Dark mode, markdown renderer, utilities
│       └── chat.js               # Chat interface logic
│
├── profiles/                     # Auto-created: student profiles (JSON)
├── logs/                         # Auto-created: application logs
└── README.md
```

---

## Quick Start (Local)

### Prerequisites

- Python 3.9+
- IBM Cloud account with watsonx.ai access
- IBM API Key and watsonx.ai Project ID

### Step 1 — Clone or Download

```bash
cd PlacementPilot
```

### Step 2 — Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Configure Environment

```bash
cp .env.example .env
```

Open `.env` and fill in your credentials:

```env
IBM_API_KEY=your_ibm_cloud_api_key_here
WATSONX_PROJECT_ID=your_watsonx_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
FLASK_SECRET_KEY=your-random-secret-key-here
```

### Step 5 — Run the Application

```bash
python app.py
```

Open your browser at: **http://localhost:5000**

---

## IBM watsonx.ai Configuration

### Getting Your IBM API Key

1. Log in to [IBM Cloud](https://cloud.ibm.com)
2. Go to **Manage → Access (IAM) → API Keys**
3. Click **Create an IBM Cloud API Key**
4. Copy and save the key securely

### Getting Your watsonx.ai Project ID

1. Go to [IBM watsonx.ai](https://dataplatform.cloud.ibm.com)
2. Open or create a project
3. Go to **Project Settings → General**
4. Copy the **Project ID**

### Supported Granite Models

| Model ID | Best For |
|----------|----------|
| `ibm/granite-3-3-8b-instruct` | Chat, reasoning, career guidance (default) |
| `ibm/granite-3-3-2b-instruct` | Faster responses, lighter workloads |
| `ibm/granite-3-0-8b-instruct` | Alternative instruct model |

Change the model in `.env`:
```env
GRANITE_MODEL_ID=ibm/granite-3-3-8b-instruct
```

---

## Customizing the AI Agent

All agent behavior is controlled in **`agent_instructions.py`**. No code changes needed elsewhere.

### What You Can Customize

```python
# ── Communication Style ─────────────────────────────────────
COMMUNICATION_STYLE = """
- Be concise and encouraging...
- Use bullet points for roadmaps...
"""

# ── Response Tone ───────────────────────────────────────────
RESPONSE_TONE = """
- Professional yet friendly...
"""

# ── Expertise Domains ───────────────────────────────────────
EXPERTISE_DOMAINS = [
    "DSA & Algorithms",
    "System Design",
    ...
]

# ── Company-Specific Guidance ───────────────────────────────
COMPANY_GUIDANCE = {
    "Google": {
        "focus": "DSA (hard level), system design...",
        "rounds": "Online test → Phone screen → 4-5 onsite",
        "tips": "Practice LeetCode hard...",
    },
    # Add your custom company here!
}

# ── Safety Rules ────────────────────────────────────────────
SAFETY_RULES = """
1. Only answer placement-related questions...
"""
```

### Adding a New Company

In `agent_instructions.py`, add to `COMPANY_GUIDANCE`:
```python
"YourCompany": {
    "focus": "Topics to study",
    "rounds": "Round 1 → Round 2 → HR",
    "tips": "Company-specific preparation tips",
},
```

---

## Module Reference

### AI Chat Modules

| Module Key | Focus |
|------------|-------|
| `general` | Open-ended placement advice |
| `dsa` | Data structures, algorithms, coding |
| `roadmap` | Preparation roadmap generation |
| `resume` | Resume analysis and improvement |
| `interview` | Mock interview questions |
| `hr` | Behavioral and HR preparation |
| `aptitude` | Quantitative and logical practice |
| `company` | Company-specific strategies |
| `projects` | Portfolio and project ideas |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | General AI chat |
| `/api/generate-roadmap` | POST | Generate placement roadmap |
| `/api/analyze-resume` | POST | Analyze resume text |
| `/api/mock-interview` | POST | Generate interview questions |
| `/api/aptitude-quiz` | POST | Generate aptitude questions |
| `/api/project-recommendations` | POST | Recommend projects |
| `/api/dsa-plan` | POST | Generate DSA study plan |
| `/api/update-progress` | POST | Update preparation progress |

---

## Deployment on IBM Cloud

### Option A — IBM Cloud Foundry

**1. Install IBM Cloud CLI:**
```bash
# Download from https://cloud.ibm.com/docs/cli
ibmcloud login
ibmcloud target --cf
```

**2. Create `manifest.yml` in the project root:**
```yaml
applications:
  - name: placement-pilot-ai
    memory: 512M
    instances: 1
    buildpack: python_buildpack
    command: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
    env:
      IBM_API_KEY: your_key
      WATSONX_PROJECT_ID: your_project_id
      WATSONX_URL: https://us-south.ml.cloud.ibm.com
      FLASK_SECRET_KEY: your_secret_key
      FLASK_ENV: production
      FLASK_DEBUG: "False"
```

**3. Create `Procfile`:**
```
web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

**4. Deploy:**
```bash
ibmcloud cf push
```

### Option B — IBM Code Engine (Container)

**1. Create `Dockerfile`:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p profiles logs
EXPOSE 8080
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120"]
```

**2. Build and push:**
```bash
docker build -t placement-pilot-ai .
ibmcloud cr login
docker tag placement-pilot-ai us.icr.io/your-namespace/placement-pilot-ai
docker push us.icr.io/your-namespace/placement-pilot-ai
```

**3. Deploy to Code Engine:**
```bash
ibmcloud ce project create --name placement-pilot
ibmcloud ce application create \
  --name placement-pilot-ai \
  --image us.icr.io/your-namespace/placement-pilot-ai \
  --env IBM_API_KEY=your_key \
  --env WATSONX_PROJECT_ID=your_project_id \
  --env FLASK_SECRET_KEY=your_secret \
  --port 8080
```

### Option C — IBM Cloud Kubernetes Service

```bash
# Apply deployment
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `IBM_API_KEY` | ✅ Yes | IBM Cloud API Key |
| `WATSONX_PROJECT_ID` | ✅ Yes | watsonx.ai Project ID |
| `WATSONX_URL` | ✅ Yes | watsonx.ai endpoint URL |
| `GRANITE_MODEL_ID` | No | Granite model ID (default: granite-3-3-8b-instruct) |
| `FLASK_SECRET_KEY` | ✅ Yes | Flask session encryption key |
| `FLASK_ENV` | No | `development` or `production` |
| `FLASK_DEBUG` | No | `True` or `False` |
| `FLASK_PORT` | No | Port number (default: 5000) |
| `SESSION_LIFETIME_MINUTES` | No | Session duration (default: 120) |
| `MAX_CHAT_HISTORY` | No | Max messages to retain (default: 50) |
| `LOG_LEVEL` | No | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOG_FILE` | No | Log file path (default: logs/placementpilot.log) |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI Model** | IBM Granite 3.3 8B Instruct |
| **AI Platform** | IBM watsonx.ai |
| **Backend** | Python 3.11 + Flask 3.0 |
| **Frontend** | Bootstrap 5.3 + Custom CSS |
| **Charts** | Chart.js 4.4 |
| **Icons** | Bootstrap Icons 1.11 |
| **Fonts** | Google Fonts — Inter |
| **Session** | Flask server-side sessions |
| **Storage** | JSON file-based profile store |
| **Deployment** | IBM Cloud Foundry / Code Engine |

---

## Security Notes

- ✅ IBM API Key stored in `.env` file (never in code)
- ✅ Flask sessions encrypted with `SECRET_KEY`
- ✅ Input sanitization via HTML escaping
- ✅ AI safety rules in `agent_instructions.py`
- ✅ No user passwords stored (profile-only system)
- ✅ `.env` included in `.gitignore`
- ⚠️ Add HTTPS in production (IBM Cloud handles this automatically)

---

## Troubleshooting

**Q: AI responses return "Demo Mode" message**  
A: Your `IBM_API_KEY` or `WATSONX_PROJECT_ID` is missing/invalid in `.env`. Verify them at IBM Cloud console.

**Q: `ModuleNotFoundError: ibm_watsonx_ai`**  
A: Run `pip install -r requirements.txt` in your virtual environment.

**Q: Session keeps expiring**  
A: Increase `SESSION_LIFETIME_MINUTES` in `.env`.

**Q: Port 5000 already in use**  
A: Change `FLASK_PORT=5001` in `.env`.

---

## License

MIT License — Free to use, modify, and deploy for educational purposes.

---

<div align="center">
  <strong>PlacementPilot AI</strong> · Powered by IBM Granite · IBM watsonx.ai<br/>
  Built for campus placement success 🚀
</div>
