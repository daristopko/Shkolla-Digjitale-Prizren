# AURA: Autonomous Instagram AI Agent 🤖✨

AURA is a complete, production-ready, 100% Python-based autonomous agent application designed to manage Instagram accounts. Built on top of **Streamlit** for a premium user experience, **instagrapi** for session-based Instagram connections, and **OpenAI GPT** for content strategy, generation, and conversational direct message/comment responses.

AURA supports a robust **Simulation Mode** out-of-the-box. If live credentials are not supplied, it functions completely on simulated endpoints, allowing local developers to test all dashboard tabs, post scheduling, and smart automation triggers immediately without triggering Instagram block points.

---

## Features

* **📊 High-End Analytics Dashboard**: Features glassmorphic cards and interactive graphs showcasing followers growth, post reach, and average engagement rate using Plotly.
* **🎯 Content Strategy Planner**: Set and save brand parameters (Niche, Tone, Target Audience, Pillars) and generate AI-driven strategic content topics.
* **📅 Autonomous Post Scheduler**: Automatically schedules posts. If no image asset is uploaded, AURA auto-generates custom, abstract high-resolution typography cards containing post topics to prevent errors.
* **💬 Intelligent Direct Engagement Inbox**: Simulates or reads active DMs and comments, writes contextual replies matching the brand tone, and automates replies upon authorization.
* **🔐 Secure API isolation**: Centralized configuration with highlighted start/end tags for easy credential replacements.

---

## Installation & Setup

### 1. Install Dependencies
Ensure you have Python 3.9+ installed. Run the following command to install the required libraries:
```bash
pip install -r requirements.txt
```

*Note: For image placeholder rendering, PIL is used (installed via `pillow`). For live OTP generators, `pyotp` is supported.*

### 2. Run the App
Launch the Streamlit dashboard on your local machine:
```bash
streamlit run app.py
```
This opens the web browser automatically to the dashboard at `http://localhost:8501`.

---

## API Configuration

To switch AURA from simulation mode to a live Instagram account and real OpenAI AI responses, set environment variables before starting Streamlit. Do not place live credentials directly in `config.py`.

```powershell
$env:OPENAI_API_KEY = "sk-..."
$env:INSTAGRAM_USERNAME = "your_handle"
$env:INSTAGRAM_PASSWORD = "your_password"
$env:INSTAGRAM_2FA_SEED = "optional_totp_seed"
$env:SIMULATION_MODE = "False"
```

* **Live Authentication**: AURA handles session serialization automatically. Upon logging in, it saves per-account session profiles under `media/sessions/` to prevent spam logins and security checkpoints.
* **2FA Support**: If your Instagram account has 2FA enabled, provide the TOTP seed through `INSTAGRAM_2FA_SEED`. AURA will auto-generate one-time codes on login.

---

## File Structure

* [`app.py`](file:///c:/Users/User/Desktop/Python-project/app.py): The main Streamlit web application with custom dark theme overlays, scheduling mechanisms, and UI tabs.
* [`agent.py`](file:///c:/Users/User/Desktop/Python-project/agent.py): Holds the generative agent orchestration and rules-based fallback engines.
* [`instagram_client.py`](file:///c:/Users/User/Desktop/Python-project/instagram_client.py): Controls live Instagram interactions (`instagrapi.Client`) and handles simulated mocks.
* [`database.py`](file:///c:/Users/User/Desktop/Python-project/database.py): Manages local SQLite schema and updates via SQLAlchemy.
* [`config.py`](file:///c:/Users/User/Desktop/Python-project/config.py): Loads runtime configuration from environment variables.
