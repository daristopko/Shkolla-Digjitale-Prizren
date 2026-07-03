import os

# =====================================================================
# # API_CONFIG_START
# =====================================================================
# Centralized Configuration Management
# These values load from your system's environment variables if present.
# Defaults are intentionally non-secret placeholders.

# OpenAI API Key for content generation and auto-engagement
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Instagram Credentials (used by instagrapi)
INSTAGRAM_USERNAME = os.environ.get("INSTAGRAM_USERNAME", "")
INSTAGRAM_PASSWORD = os.environ.get("INSTAGRAM_PASSWORD", "")

# Optional: 2FA TOTP Seed (if 2FA is active on your Instagram account, instagrapi can auto-generate codes)
INSTAGRAM_2FA_SEED = os.environ.get("INSTAGRAM_2FA_SEED", "")

# Operational Mode
# Switch this to False when you are ready to transition from sandbox simulation to live API execution.
SIMULATION_MODE = os.environ.get("SIMULATION_MODE", "True").lower() in ("true", "1", "yes")
# =====================================================================
# # API_CONFIG_END
# =====================================================================

# Local database file path for content strategy tracking & engagement memory logs
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///instagram_agent.db")
