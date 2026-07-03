"""
AURA Control Portal — app.py
Full-stack Instagram AI Operations Hub built on Streamlit + instagrapi + OpenAI GPT-4o.
"""

import os
import random
import json
import hashlib
import re
import traceback
import importlib
import io
import textwrap
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

# ── Internal modules ──────────────────────────────────────────────────────────
import config
import database as db_models

db_models = importlib.reload(db_models)
init_db = db_models.init_db
SessionLocal = db_models.SessionLocal
Post = db_models.Post
ScheduledPost = db_models.ScheduledPost
Strategy = db_models.Strategy
EngagementLog = db_models.EngagementLog
AnalyticsSnapshot = db_models.AnalyticsSnapshot
AutopilotRule = db_models.AutopilotRule
AccountProfile = db_models.AccountProfile
import agent as agent_module

agent_module = importlib.reload(agent_module)
AIAgent = agent_module.AIAgent

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG   (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AURA Control Portal",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

os.makedirs("media", exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

html, body, [class*=\"css\"] { font-family: 'Outfit', sans-serif; color: #f3f4f6; }

.stApp {
    background-color: #060810;
    background-image:
        radial-gradient(ellipse 80% 60% at 10% 5%,  rgba(124,58,237,.07) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 90% 90%, rgba(6,182,212,.06)  0%, transparent 55%);
}
#MainMenu, footer { visibility: hidden; }

/* ── Glass card ── */
.glass-card {
    background: rgba(17,24,39,.65);
    border: 1px solid rgba(255,255,255,.06);
    border-radius: 18px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,.35);
    backdrop-filter: blur(10px);
    transition: border-color .3s ease, box-shadow .3s ease, transform .25s ease;
}
.glass-card:hover {
    border-color: rgba(139,92,246,.35);
    box-shadow: 0 12px 40px rgba(139,92,246,.12);
    transform: translateY(-2px);
}

/* ── Login portal ── */
.portal-wrapper { max-width: 520px; margin: 60px auto 0 auto; }
.portal-title {
    background: linear-gradient(135deg, #c084fc 0%, #6366f1 60%, #06b6d4 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-size: 3rem; font-weight: 800; letter-spacing: -.04em; text-align: center; margin: 0;
}
.portal-subtitle {
    color: #6b7280; text-align: center; font-size: .95rem;
    letter-spacing: .12em; text-transform: uppercase; margin: 6px 0 32px;
}
.portal-divider { border: none; border-top: 1px solid rgba(255,255,255,.06); margin: 22px 0; }

/* ── Gradient text ── */
.gradient-header {
    background: linear-gradient(135deg, #c084fc 0%, #6366f1 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-weight: 800; font-size: 2rem; letter-spacing: -.03em;
}

/* ── Metric card ── */
.metric-container { display:flex; flex-direction:column; align-items:center; text-align:center; padding:16px 8px; }
.metric-value {
    font-size: 1.9rem; font-weight: 800;
    background: linear-gradient(135deg, #a78bfa 0%, #06b6d4 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 4px; letter-spacing: -.02em;
}
.metric-lbl { font-size: .78rem; color: #6b7280; text-transform: uppercase; letter-spacing: .12em; font-weight: 600; }

/* ── Status pills ── */
.status-pill { display:inline-flex; align-items:center; gap:6px; padding:5px 14px; border-radius:9999px; font-size:.78rem; font-weight:600; }
.status-live    { background:rgba(16,185,129,.1); color:#10b981; border:1px solid rgba(16,185,129,.25); }
.status-sandbox { background:rgba(245,158,11,.1); color:#f59e0b; border:1px solid rgba(245,158,11,.25); }
.status-error   { background:rgba(239,68,68,.1);  color:#ef4444; border:1px solid rgba(239,68,68,.25); }
.status-info    { background:rgba(99,102,241,.1); color:#818cf8; border:1px solid rgba(99,102,241,.25); }

/* ── Account banner ── */
.account-banner {
    display:flex; align-items:center; gap:18px;
    padding:16px 24px;
    background:rgba(17,24,39,.7); border:1px solid rgba(255,255,255,.06);
    border-radius:16px; margin-bottom:22px; backdrop-filter:blur(10px);
}
.account-handle {
    font-size:1.35rem; font-weight:700;
    background:linear-gradient(90deg,#a78bfa,#06b6d4);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.account-bio { font-size:.83rem; color:#6b7280; margin-top:2px; }

/* ── Buttons ── */
div.stButton > button:first-child {
    background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%);
    color: white; border: none; border-radius: 10px; padding: 10px 24px;
    font-weight: 600; font-size: .92rem; box-shadow: 0 4px 14px rgba(124,58,237,.4);
    transition: all .2s ease; width: 100%;
}
div.stButton > button:first-child:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 22px rgba(124,58,237,.6);
    background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
}
.bypass-btn > button:first-child {
    background: rgba(255,255,255,.04) !important; border: 1px solid rgba(255,255,255,.1) !important;
    box-shadow: none !important; color: #6b7280 !important; font-size: .82rem !important;
}
.bypass-btn > button:first-child:hover {
    border-color: rgba(245,158,11,.4) !important; color: #f59e0b !important;
    transform: none !important; background: rgba(245,158,11,.06) !important;
}
.scan-btn > button:first-child {
    background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
    box-shadow: 0 4px 14px rgba(16,185,129,.35) !important;
}
.scan-btn > button:first-child:hover {
    background: linear-gradient(135deg, #10b981 0%, #34d399 100%) !important;
    box-shadow: 0 6px 22px rgba(16,185,129,.5) !important;
}
.danger-btn > button:first-child {
    background: rgba(239,68,68,.12) !important; border: 1px solid rgba(239,68,68,.25) !important;
    box-shadow: none !important; color: #f87171 !important;
}

/* ── Inputs ── */
input[type="text"], input[type="password"] {
    background: rgba(255,255,255,.04) !important;
    border: 1px solid rgba(255,255,255,.1) !important;
    border-radius: 10px !important; color: #f3f4f6 !important;
}
input[type="text"]:focus, input[type="password"]:focus {
    border-color: rgba(139,92,246,.5) !important;
    box-shadow: 0 0 0 3px rgba(139,92,246,.12) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(17,24,39,.5); border-radius:12px; padding:4px; gap:4px;
    border:1px solid rgba(255,255,255,.06);
}
.stTabs [data-baseweb="tab"] { border-radius:8px; color:#6b7280; font-weight:600; padding:10px 20px; transition:all .2s; }
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    color: white !important; box-shadow: 0 4px 14px rgba(124,58,237,.35);
}

/* ── Telemetry sidebar ── */
.tele-entry {
    padding: 8px 10px; border-radius:8px;
    background: rgba(255,255,255,.03); border-left:3px solid;
    margin-bottom:8px; font-size:.78rem; line-height:1.5;
}
.tele-ok    { border-color:#10b981; }
.tele-warn  { border-color:#f59e0b; }
.tele-error { border-color:#ef4444; }
.tele-info  { border-color:#6366f1; }

/* ── Grid telemetry card ── */
.grid-card {
    border-radius:14px; overflow:hidden;
    border:1px solid rgba(255,255,255,.07);
    background:rgba(17,24,39,.6);
    transition: transform .25s ease, box-shadow .25s ease;
}
.grid-card:hover { transform:scale(1.02); box-shadow:0 12px 36px rgba(139,92,246,.15); }

/* ── Format selector ── */
.format-badge {
    display:inline-flex; align-items:center; gap:6px;
    padding:4px 12px; border-radius:8px; font-size:.78rem; font-weight:600;
    background:rgba(139,92,246,.15); color:#a78bfa; border:1px solid rgba(139,92,246,.25);
    margin-right:6px;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE BOOTSTRAP
# ─────────────────────────────────────────────────────────────────────────────
_DEFAULTS = {
    "authenticated": False,
    "ig_client": None,
    "live_profile": None,
    "active_account_id": None,
    "active_account_label": "",
    "session_handshake_verified": False,
    "account_action_clock": {},
    "is_sandbox": False,
    "auth_error": None,
    "draft_caption": "",
    "draft_hashtags": "",
    "draft_media": "",
    "draft_language": "English",
    "draft_image_style": "text",
    "telemetry": [],          # list of {ts, level, msg}
    "scan_running": False,
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ─────────────────────────────────────────────────────────────────────────────
# DATABASE + AGENT
# ─────────────────────────────────────────────────────────────────────────────
init_db()
db = SessionLocal()
agent = AIAgent(db, st.session_state.get("active_account_id") or "default")


# ─────────────────────────────────────────────────────────────────────────────
# TELEMETRY HELPER
# ─────────────────────────────────────────────────────────────────────────────
def _log(msg: str, level: str = "info") -> None:
    """Appends a timestamped entry to the in-session telemetry log."""
    ts = datetime.utcnow().strftime("%H:%M:%S")
    st.session_state.telemetry.insert(0, {"ts": ts, "level": level, "msg": msg})
    # Keep last 60 entries
    st.session_state.telemetry = st.session_state.telemetry[:60]


def _account_id_for(username: str, mode: str = "live") -> str:
    clean = re.sub(r"[^a-z0-9_]+", "_", (username or "account").strip().lower().lstrip("@"))
    digest = hashlib.sha256(f"{mode}:{clean}".encode("utf-8")).hexdigest()[:10]
    return f"{mode}_{clean[:42]}_{digest}"


def _session_path_for(account_id: str) -> str:
    session_dir = Path("media") / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)
    return str(session_dir / f"{account_id}.json")


def _clear_account_temp_state() -> None:
    prefixes = ("draft_", "dm_draft_", "dm_ta_", "comm_draft_", "comm_ta_")
    for key in list(st.session_state.keys()):
        if key.startswith(prefixes):
            del st.session_state[key]


def _upsert_account_profile(account_id: str, profile: dict, session_mode: str, last_error: str = None) -> None:
    row = db.query(AccountProfile).filter(AccountProfile.account_id == account_id).first()
    if not row:
        row = AccountProfile(account_id=account_id)
        db.add(row)
    row.username = profile.get("username") or account_id
    row.display_name = profile.get("full_name") or row.username
    row.session_mode = session_mode
    row.status = "error" if last_error else "active"
    row.last_error = last_error
    row.last_verified_at = datetime.utcnow()
    db.commit()


def _set_active_account(account_id: str, profile: dict, client, is_sandbox: bool) -> None:
    previous_id = st.session_state.get("active_account_id")
    if previous_id and previous_id != account_id:
        _clear_account_temp_state()
    st.session_state.active_account_id = account_id
    st.session_state.active_account_label = f"@{profile.get('username', account_id)}"
    st.session_state.session_handshake_verified = False
    st.session_state.ig_client = client
    st.session_state.live_profile = profile
    st.session_state.authenticated = True
    st.session_state.is_sandbox = is_sandbox


def _active_account_id() -> str:
    return st.session_state.get("active_account_id") or "default"


def _active_query(model):
    return db.query(model).filter(model.account_id == _active_account_id())


def _require_verified_account(action: str, write_action: bool = False) -> bool:
    account_id = _active_account_id()
    profile = st.session_state.get("live_profile") or {}
    expected_label = st.session_state.get("active_account_label") or f"@{profile.get('username', account_id)}"
    if not st.session_state.get("session_handshake_verified"):
        st.error(f"Verify the active target account before {action}: {expected_label}")
        _log(f"Blocked {action}: account handshake missing for {account_id}", "warn")
        return False
    if write_action:
        now = datetime.utcnow()
        clock = st.session_state.account_action_clock
        last_iso = clock.get(account_id)
        if last_iso:
            last_dt = datetime.fromisoformat(last_iso)
            wait = 8 - (now - last_dt).total_seconds()
            if wait > 0:
                st.warning(f"Rate limit guard: wait {wait:.0f}s before another write for {expected_label}.")
                return False
        clock[account_id] = now.isoformat()
        st.session_state.account_action_clock = clock
    return True


def _mark_account_error(error, action: str) -> None:
    account_id = _active_account_id()
    profile = st.session_state.get("live_profile") or {}
    err_text = str(error)
    _upsert_account_profile(
        account_id,
        profile or {"username": account_id},
        "sandbox" if st.session_state.get("is_sandbox") else "live",
        f"{action}: {err_text}",
    )
    _log(f"{action} halted for {account_id}: {err_text}", "error")


def _account_write_allowed(action: str, min_interval_seconds: int = 8) -> bool:
    account_id = _active_account_id()
    now = datetime.utcnow()
    clock = st.session_state.account_action_clock
    last_iso = clock.get(account_id)
    if last_iso:
        try:
            last_dt = datetime.fromisoformat(last_iso)
            wait = min_interval_seconds - (now - last_dt).total_seconds()
        except ValueError:
            wait = 0
        if wait > 0:
            _log(f"Rate guard paused {action} for {_active_account_id()} ({wait:.0f}s remaining).", "warn")
            return False
    clock[account_id] = now.isoformat()
    st.session_state.account_action_clock = clock
    return True


# ─────────────────────────────────────────────────────────────────────────────
# IMAGE GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
def create_gradient_post_image(topic: str, text_caption: str, filepath: str) -> str:
    img = Image.new("RGB", (1080, 1080), "#0f111a")
    draw = ImageDraw.Draw(img)
    for _ in range(3):
        x = random.randint(100, 980); y = random.randint(100, 980); r = random.randint(200, 450)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=random.choice(["#7c3aed","#06b6d4","#ec4899","#8b5cf6"]))
    overlay = Image.new("RGBA", (1080, 1080), (15, 17, 26, 210))
    img.paste(overlay, (0, 0), overlay)
    draw.rounded_rectangle([(40,40),(1040,1040)], radius=24, outline=(255, 255, 255, 26), width=3)
    draw.text((80, 100), "AUTO POST · AURA AI", fill="#9ca3af")
    draw.text((80, 200), f"Topic: {(topic or 'Insight').upper()}", fill="#06b6d4")
    draw.rectangle([(70, 80), (980, 260)], fill="#0f111a")
    draw.text((80, 160), f"{(topic or 'Insight').upper()}", fill="#06b6d4")
    words = text_caption.split(); lines, cur = [], []
    for word in words:
        if len(" ".join(cur + [word])) < 35: cur.append(word)
        else: lines.append(" ".join(cur)); cur = [word]
    if cur: lines.append(" ".join(cur))
    y_off = 350
    for line in lines[:10]: draw.text((80, y_off), line, fill="#ffffff"); y_off += 55
    img.save(filepath)
    return filepath


# ─────────────────────────────────────────────────────────────────────────────
# DB HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _font(size: int, bold: bool = False):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
    ]
    for font_path in candidates:
        try:
            return ImageFont.truetype(font_path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap_for_font(draw, text: str, font, max_width: int, max_lines: int) -> list:
    words = (text or "").replace("\n", " ").split()
    lines, current = [], ""
    for word in words:
        test = f"{current} {word}".strip()
        if draw.textbbox((0, 0), test, font=font)[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
        if len(lines) >= max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(current)
    if len(lines) == max_lines and len(" ".join(words)) > len(" ".join(lines)):
        lines[-1] = lines[-1].rstrip(".") + "..."
    return lines


def _topic_photo(topic: str, visual_prompt: str = ""):
    query = urllib.parse.quote_plus((visual_prompt or topic or "technology workspace").strip())
    url = f"https://source.unsplash.com/1080x1080/?{query}"
    req = urllib.request.Request(url, headers={"User-Agent": "AURA-Control-Portal/1.0"})
    with urllib.request.urlopen(req, timeout=12) as response:
        data = response.read()
    return Image.open(io.BytesIO(data)).convert("RGB").resize((1080, 1080), Image.Resampling.LANCZOS)


def create_gradient_post_image(
    topic: str,
    text_caption: str,
    filepath: str,
    visual_prompt: str = "",
    use_web_photo: bool = False,
    visual_mode: str = "text",
) -> str:
    # Upgrade: generated photo posts stay purely visual; text posts use a simple premium card.
    visual_mode = (visual_mode or "text").lower()
    photo_only = visual_mode == "photo"
    used_photo = False
    if use_web_photo or photo_only:
        try:
            img = _topic_photo(topic, visual_prompt)
            img = ImageEnhance.Color(img).enhance(1.12)
            img = ImageEnhance.Contrast(img).enhance(1.08)
            if not photo_only:
                img = img.filter(ImageFilter.GaussianBlur(radius=0.35))
            used_photo = True
        except Exception as fetch_err:
            _log(f"Web image fetch failed, using designed card: {fetch_err}", "warn")
            img = Image.new("RGB", (1080, 1080), "#10131f")
    else:
        img = Image.new("RGB", (1080, 1080), "#10131f")

    if photo_only and used_photo:
        draw = ImageDraw.Draw(img, "RGBA")
        draw.rectangle([(0, 0), (1080, 1080)], fill=(0, 0, 0, 14))
        img.convert("RGB").save(filepath, quality=96)
        return filepath

    draw = ImageDraw.Draw(img, "RGBA")
    if not used_photo:
        palette = ["#2563eb", "#06b6d4", "#ef4444", "#f59e0b", "#10b981"]
        for _ in range(7):
            x = random.randint(-120, 1080)
            y = random.randint(-120, 1080)
            r = random.randint(180, 420)
            draw.ellipse([x-r, y-r, x+r, y+r], fill=random.choice(palette) + "44")
        img = img.filter(ImageFilter.GaussianBlur(radius=26))
        draw = ImageDraw.Draw(img, "RGBA")

    draw.rectangle([(0, 0), (1080, 1080)], fill=(8, 12, 22, 112 if used_photo else 72))
    draw.rectangle([(0, 620), (1080, 1080)], fill=(4, 8, 16, 205))
    draw.rounded_rectangle([(56, 56), (1024, 1024)], radius=36, outline=(255, 255, 255, 34), width=3)
    draw.rounded_rectangle([(82, 82), (330, 132)], radius=24, fill=(255, 255, 255, 28))

    eyebrow_font = _font(28, bold=True)
    title_font = _font(68, bold=True)
    body_font = _font(40)
    footer_font = _font(27, bold=True)

    clean_topic = (topic or "Insight").strip()
    draw.text((108, 94), "AURA AI POST", font=eyebrow_font, fill=(226, 232, 240, 230))
    draw.rectangle([(90, 88), (380, 138)], fill=(8, 12, 22, 255))
    title_lines = _wrap_for_font(draw, clean_topic.upper(), title_font, 900, 2)
    title_y = 174
    for title_line in title_lines:
        draw.text((82, title_y), title_line, font=title_font, fill=(255, 255, 255, 255))
        title_y += 82

    caption = (text_caption or "A clear, practical insight for your audience.").split("#")[0].strip()
    lines = _wrap_for_font(draw, caption, body_font, 880, 5)
    y_off = 666
    for line in lines:
        draw.text((84, y_off), line, font=body_font, fill=(248, 250, 252, 245))
        y_off += 58

    draw.line([(84, 948), (330, 948)], fill=(6, 182, 212, 220), width=6)
    draw.text((84, 970), "DESIGNED FOR INSTAGRAM", font=footer_font, fill=(203, 213, 225, 220))

    draw.rectangle([(80, 962), (720, 1010)], fill=(4, 8, 16, 255))
    img.convert("RGB").save(filepath, quality=95)
    return filepath


def _get_or_create_strategy() -> Strategy:
    account_id = _active_account_id()
    row = (
        db.query(Strategy)
        .filter(Strategy.account_id == account_id)
        .order_by(Strategy.id.asc())
        .first()
    )
    if not row:
        row = Strategy(account_id=account_id); db.add(row); db.commit(); db.refresh(row)
    return row


def _fetch_live_profile(cl) -> dict:
    info = cl.user_info(cl.user_id)
    return {
        "username":    info.username,
        "full_name":   info.full_name or info.username,
        "followers":   info.follower_count,
        "following":   info.following_count,
        "posts_count": info.media_count,
        "biography":   info.biography or "",
    }


# ─────────────────────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────────────────────
def _get_direct_messages(cl) -> list:
    if hasattr(cl, "get_direct_messages"):
        return cl.get_direct_messages()

    threads = cl.direct_threads(amount=10)
    unread_dms = []
    for thread in threads:
        if getattr(thread, "unread_item_count", 0) <= 0 or not getattr(thread, "messages", None):
            continue
        last_message = thread.messages[0]
        users = getattr(thread, "users", None) or []
        user = users[0] if users else None
        username = getattr(user, "username", None) or str(getattr(last_message, "user_id", "user"))
        timestamp = getattr(last_message, "timestamp", None)
        unread_dms.append({
            "id": str(thread.id),
            "username": username,
            "text": getattr(last_message, "text", "") or "",
            "timestamp": timestamp.isoformat() if timestamp else datetime.utcnow().isoformat(),
            "is_unread": True,
        })
    return unread_dms


def _reply_to_direct_message(cl, thread_id: str, text: str) -> bool:
    if hasattr(cl, "reply_to_direct_message"):
        return cl.reply_to_direct_message(thread_id, text)
    cl.direct_send(text, thread_ids=[thread_id])
    return True


def _get_recent_posts(cl, limit: int = 5) -> list:
    if hasattr(cl, "get_recent_posts"):
        return cl.get_recent_posts(limit=limit)

    medias = cl.user_medias(cl.user_id, amount=limit)
    posts = []
    for media in medias:
        thumbnail = getattr(media, "thumbnail_url", None)
        posts.append({
            "id": str(media.pk),
            "caption": getattr(media, "caption_text", "") or "",
            "like_count": getattr(media, "like_count", 0) or 0,
            "comment_count": getattr(media, "comment_count", 0) or 0,
            "media_type": "video" if getattr(media, "media_type", None) == 2 else "image",
            "thumbnail_url": str(thumbnail) if thumbnail else "https://picsum.photos/id/20/800/800",
            "taken_at": media.taken_at.isoformat() if getattr(media, "taken_at", None) else datetime.utcnow().isoformat(),
        })
    return posts


def _get_comments(cl, media_id: str) -> list:
    if hasattr(cl, "get_comments"):
        return cl.get_comments(media_id)

    comments = cl.media_comments(media_id, amount=20)
    return [{
        "id": str(comment.pk),
        "username": getattr(getattr(comment, "user", None), "username", "user"),
        "text": getattr(comment, "text", "") or "",
        "is_unread": True,
    } for comment in comments]


def _reply_to_comment(cl, media_id: str, comment_id: str, text: str) -> bool:
    if hasattr(cl, "reply_to_comment"):
        return cl.reply_to_comment(comment_id, text)
    cl.comment_create(media_id, text, replied_to_comment_id=comment_id)
    return True


def _verification_code_for(two_factor_value: str) -> str:
    value = (two_factor_value or "").strip().replace(" ", "")
    if not value:
        return ""
    if value.isdigit() and len(value) == 6:
        return value
    try:
        import pyotp
    except ImportError as exc:
        raise RuntimeError("Install pyotp or enter the current 6-digit Instagram 2FA code.") from exc
    return pyotp.TOTP(value).now()


def _challenge_code_handler_for(challenge_value: str):
    def handler(username: str, choice) -> str:
        code = _verification_code_for(challenge_value)
        if not code:
            _log(f"Instagram challenge requested for @{username}. Enter the email/SMS code and retry.", "warn")
        return code
    return handler


def _login_instagram_client(cl, username: str, password: str, two_factor_value: str = "") -> None:
    cl.challenge_code_handler = _challenge_code_handler_for(two_factor_value)
    cl.login(username, password, verification_code=_verification_code_for(two_factor_value))


def _do_live_login(username: str, password: str, two_factor_value: str = "") -> None:
    st.session_state.auth_error = None
    account_id = _account_id_for(username, "live")
    session_path = _session_path_for(account_id)
    try:
        from instagrapi import Client
        cl = Client()
        if os.path.exists(session_path):
            try:
                cl.load_settings(session_path); _login_instagram_client(cl, username, password, two_factor_value); cl.get_timeline_feed()
            except Exception:
                os.remove(session_path); cl = Client(); _login_instagram_client(cl, username, password, two_factor_value)
        else:
            _login_instagram_client(cl, username, password, two_factor_value)
        cl.dump_settings(session_path)
        profile = _fetch_live_profile(cl)
        account_id = _account_id_for(profile["username"], "live")
        account_session_path = _session_path_for(account_id)
        if session_path != account_session_path:
            cl.dump_settings(account_session_path)
        _upsert_account_profile(account_id, profile, "live")
        _set_active_account(account_id, profile, cl, False)
        _log(f"Live auth success: @{profile['username']}", "ok")
        st.rerun()
    except Exception as err:
        st.session_state.auth_error = str(err)
        _upsert_account_profile(account_id, {"username": username}, "live", str(err))
        _log(f"Auth failed: {err}", "error")


def _do_sandbox_bypass() -> None:
    from instagram_client import MockInstagramClient
    mock = MockInstagramClient(username=config.INSTAGRAM_USERNAME or "sandbox_agent")
    profile = mock.get_profile_info()
    account_id = _account_id_for(profile["username"], "sandbox")
    _upsert_account_profile(account_id, profile, "sandbox")
    _set_active_account(account_id, profile, mock, True)
    _log("Sandbox bypass activated — no real API calls made.", "warn")
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# AUTOPILOT SCAN ENGINE
# ─────────────────────────────────────────────────────────────────────────────
def _rule_matches(text: str, rule: AutopilotRule) -> bool:
    text_l = text.lower()
    for kw in rule.keyword.split(","):
        if kw.strip().lower() in text_l:
            return True
    return False


def _format_template(template: str, username: str) -> str:
    return template.replace("{username}", f"@{username}")


def run_autopilot_scan(ig_cl, rules: list, strategy: Strategy) -> dict:
    """
    Runs the full autopilot pass:
      1. Downloads DM threads via direct_threads / get_direct_messages
      2. Fetches recent media + comments via user_medias / media_comments (live)
         or get_recent_posts / get_comments (mock)
      3. For each unread DM / un-replied comment:
         - Check rulebook first; if a rule fires → use its template
         - Otherwise → GPT-4o (or simulated agent)
      4. Pushes replies and logs to DB
    Returns a summary dict {dm_replied, comment_replied, errors}.
    """
    result = {"dm_replied": 0, "comment_replied": 0, "errors": []}
    account_id = _active_account_id()
    dm_rules      = [r for r in rules if r.scope in ("dm",      "both") and r.active]
    comment_rules = [r for r in rules if r.scope in ("comment", "both") and r.active]

    # ── 1. DIRECT MESSAGES ──────────────────────────────────────────────────
    try:
        dms = _get_direct_messages(ig_cl)
        unread_dms = [d for d in dms if d.get("is_unread")]
        for dm in unread_dms:
            mid   = dm.get("id", "")
            uname = dm.get("username", "user")
            text  = dm.get("text", "")

            # Already logged?
            exists = db.query(EngagementLog).filter(
                EngagementLog.account_id == account_id,
                EngagementLog.message_id == mid,
                EngagementLog.type == "dm"
            ).first()
            if exists:
                continue

            # Rule match → template; else AI
            reply = None
            for rule in dm_rules:
                if _rule_matches(text, rule):
                    reply = _format_template(rule.response_template, uname)
                    _log(f"[Autopilot·DM] Rule '{rule.name}' matched @{uname}", "info")
                    break
            if not reply:
                reply = agent.generate_dm_reply(text, uname)

            try:
                if not _account_write_allowed(f"autopilot DM reply to @{uname}"):
                    result["errors"].append(f"DM rate guard paused before @{uname}; rerun later.")
                    continue
                ok = _reply_to_direct_message(ig_cl, mid, reply)
                if ok:
                    db.add(EngagementLog(
                        account_id=account_id,
                        type="dm", username=uname, message_id=mid,
                        input_text=text, response_text=reply, status="sent", autopilot=True
                    ))
                    db.commit()
                    result["dm_replied"] += 1
                    _log(f"[Autopilot·DM] Replied to @{uname}", "ok")
            except Exception as send_err:
                _mark_account_error(send_err, "Autopilot DM send")
                result["errors"].append(f"DM send fail ({uname}): {send_err}")
                _log(f"[Autopilot·DM] Send error: {send_err}", "error")

    except Exception as dm_err:
        _mark_account_error(dm_err, "Autopilot DM fetch")
        result["errors"].append(f"DM fetch: {dm_err}")
        _log(f"[Autopilot·DM] Fetch error: {dm_err}", "error")

    # ── 2. POST COMMENTS ────────────────────────────────────────────────────
    try:
        posts = _get_recent_posts(ig_cl, limit=5)
        for post in posts:
            pid = post.get("id", "")
            try:
                comments = _get_comments(ig_cl, pid)
            except Exception as ce:
                _log(f"[Autopilot·Comment] get_comments error: {ce}", "warn")
                continue

            for comm in comments:
                cid   = comm.get("id", "")
                uname = comm.get("username", "user")
                text  = comm.get("text", "")

                exists = db.query(EngagementLog).filter(
                    EngagementLog.account_id == account_id,
                    EngagementLog.message_id == str(cid),
                    EngagementLog.type == "comment"
                ).first()
                if exists:
                    continue

                reply = None
                for rule in comment_rules:
                    if _rule_matches(text, rule):
                        reply = _format_template(rule.response_template, uname)
                        _log(f"[Autopilot·Comment] Rule '{rule.name}' matched @{uname}", "info")
                        break
                if not reply:
                    reply = agent.generate_comment_reply(text, uname)

                try:
                    if not _account_write_allowed(f"autopilot comment reply to @{uname}"):
                        result["errors"].append(f"Comment rate guard paused before @{uname}; rerun later.")
                        continue
                    ok = _reply_to_comment(ig_cl, pid, str(cid), reply)
                    if ok:
                        db.add(EngagementLog(
                            account_id=account_id,
                            type="comment", username=uname, message_id=str(cid),
                            input_text=text, response_text=reply, status="sent", autopilot=True
                        ))
                        db.commit()
                        result["comment_replied"] += 1
                        _log(f"[Autopilot·Comment] Replied to @{uname} on post {pid}", "ok")
                except Exception as send_err:
                    _mark_account_error(send_err, "Autopilot comment send")
                    result["errors"].append(f"Comment reply fail ({uname}): {send_err}")
                    _log(f"[Autopilot·Comment] Send error: {send_err}", "error")

    except Exception as post_err:
        _mark_account_error(post_err, "Autopilot comment fetch")
        result["errors"].append(f"Post/comment fetch: {post_err}")
        _log(f"[Autopilot·Comment] Fetch error: {post_err}", "error")

    return result


# ─────────────────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
#  GATE  —  NOT AUTHENTICATED
# ══════════════════════════════════════════════════════════════════════════════
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.authenticated:

    st.markdown('<div class="portal-wrapper">', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;font-size:3.2rem;">🔮</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="portal-title">AURA</h1>', unsafe_allow_html=True)
    st.markdown('<p class="portal-subtitle">Control Portal · Device Synchronisation</p>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### 🔐 Instagram Credential Payload")

    u_in = st.text_input("Instagram Username", value=config.INSTAGRAM_USERNAME,
                         placeholder="@handle", label_visibility="collapsed")
    p_in = st.text_input("Password", value=config.INSTAGRAM_PASSWORD,
                         type="password", placeholder="Password", label_visibility="collapsed")
    t_in = st.text_input("2FA / Checkpoint Code or TOTP Seed (optional)", value=config.INSTAGRAM_2FA_SEED,
                         placeholder="Email/SMS checkpoint code, 2FA code, or TOTP seed", label_visibility="collapsed")

    st.markdown('<hr class="portal-divider">', unsafe_allow_html=True)

    if st.button("⚡  Initiate Synchronisation", use_container_width=True):
        if not u_in or not p_in:
            st.error("Username and password are required.")
        else:
            with st.spinner("Establishing secure link to Instagram API…"):
                _do_live_login(u_in.strip(), p_in, t_in.strip())

    if st.session_state.auth_error:
        st.markdown(f"""
        <div style="margin-top:14px;padding:14px 18px;border-radius:10px;
                    background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.2);
                    color:#f87171;font-size:.88rem;line-height:1.55;">
            <strong>⚠ Auth telemetry:</strong><br>{st.session_state.auth_error}
        </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="text-align:center;margin-top:16px;" class="bypass-btn">', unsafe_allow_html=True)
    if st.button("🧪  Force Demo Sandbox Bypass", use_container_width=True):
        _do_sandbox_bypass()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<p style="text-align:center;margin-top:20px;font-size:.75rem;color:#374151;">'
                'Credentials go directly to the Instagram API. Never stored externally.</p>',
                unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
#  POST-AUTH  —  Operational Workspace
# ─────────────────────────────────────────────────────────────────────────────

profile   = st.session_state.live_profile
ig_client = st.session_state.ig_client
agent     = AIAgent(db, _active_account_id())
strategy  = _get_or_create_strategy()

if not st.session_state.session_handshake_verified:
    st.markdown('<div class="portal-wrapper">', unsafe_allow_html=True)
    st.markdown('<h1 class="portal-title">Verify Target</h1>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    mode = "Sandbox" if st.session_state.is_sandbox else "Live"
    st.markdown(f"""
    <div class="account-banner" style="margin-bottom:16px;">
        <span style="font-size:2rem;">IG</span>
        <div>
            <div class="account-handle">@{profile['username']}</div>
            <div class="account-bio">Account ID: {_active_account_id()} · Mode: {mode}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.info("Confirm this target account before retrieving account data, posting, replying, scheduling, or running autopilot.")
    confirmed = st.checkbox(f"I confirm the active Target Account Profile is @{profile['username']}.")
    if st.button("Open Isolated Workspace", use_container_width=True):
        if confirmed:
            st.session_state.session_handshake_verified = True
            _log(f"Account handshake verified for @{profile['username']}", "ok")
            st.rerun()
        else:
            st.error("Please confirm the target account first.")
    if st.button("Switch / Sign Out", use_container_width=True):
        _clear_account_temp_state()
        for k in list(_DEFAULTS):
            st.session_state[k] = _DEFAULTS[k]
        st.rerun()
    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# TELEMETRY SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
LEVEL_MAP = {"ok": "tele-ok", "warn": "tele-warn", "error": "tele-error", "info": "tele-info"}
LEVEL_ICON = {"ok": "✅", "warn": "⚠️", "error": "❌", "info": "ℹ️"}

with st.sidebar:
    st.markdown("## 🔮 AURA")
    st.markdown(f"**@{profile['username']}** \n*Operational*")
    badge = '<span class="status-pill status-sandbox">⚠ Sandbox</span>' if st.session_state.is_sandbox else \
            '<span class="status-pill status-live">🟢 Live</span>'
    st.markdown(badge, unsafe_allow_html=True)
    st.divider()

    # Sign-out
    if st.button("🔓 Sign Out", use_container_width=True):
        for k in list(_DEFAULTS):
            st.session_state[k] = _DEFAULTS[k]
        st.rerun()

    st.divider()
    st.markdown("### 📡 Event Telemetry")
    if not st.session_state.telemetry:
        st.caption("No events yet.")
    else:
        for entry in st.session_state.telemetry[:30]:
            css = LEVEL_MAP.get(entry["level"], "tele-info")
            icon = LEVEL_ICON.get(entry["level"], "•")
            st.markdown(f"""
            <div class="tele-entry {css}">
                <span style="color:#6b7280;font-size:.72rem;">{entry['ts']}</span>
                {icon} {entry['msg']}
            </div>""", unsafe_allow_html=True)

    st.divider()
    if st.button("🗑 Clear Telemetry"):
        st.session_state.telemetry = []
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# ACCOUNT BANNER + LIVE METRICS
# ─────────────────────────────────────────────────────────────────────────────
sandbox_badge = (
    '<span class="status-pill status-sandbox">⚠ Demo Sandbox</span>'
    if st.session_state.is_sandbox else
    '<span class="status-pill status-live">🟢 Live Account</span>'
)
st.markdown(f"""
<div class="account-banner">
    <span style="font-size:2rem;">🔮</span>
    <div>
        <div class="account-handle">@{profile['username']}</div>
        <div class="account-bio">{profile.get('biography','') or 'AURA Autonomous Coordinator'}</div>
    </div>
    <div style="margin-left:auto;">{sandbox_badge}</div>
</div>
""", unsafe_allow_html=True)

# 4-column stat cards
m1, m2, m3, m4 = st.columns(4)
for col, (val, lbl) in zip([m1, m2, m3, m4], [
    (f"@{profile['username']}", "Authenticated Handle"),
    (f"{profile['followers']:,}", "Followers"),
    (f"{profile['following']:,}", "Following"),
    (f"{profile['posts_count']:,}", "Media Assets"),
]):
    with col:
        st.markdown(f"""
        <div class="glass-card metric-container">
            <div class="metric-value">{val}</div>
            <div class="metric-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

# ── Recent Grid Telemetry View ───────────────────────────────────────────────
with st.expander("📸  Recent Grid Telemetry — Last 3 Posts", expanded=False):
    try:
        grid_posts = _get_recent_posts(ig_client, limit=3)
        if not grid_posts:
            st.info("No posts found.")
        else:
            g1, g2, g3 = st.columns(3)
            for gcol, gpost in zip([g1, g2, g3], grid_posts[:3]):
                with gcol:
                    thumb = gpost.get("thumbnail_url", "https://picsum.photos/id/20/400/400")
                    cap   = (gpost.get("caption") or "")[:100]
                    mtype = gpost.get("media_type", "image")
                    mtype_icon = "🎬" if mtype == "video" else "🖼️"
                    likes  = gpost.get("like_count",    0)
                    comms  = gpost.get("comment_count", 0)
                    st.markdown(f"""
                    <div class="grid-card">
                        <img src="{thumb}" style="width:100%; height:180px; object-fit:cover;" />
                        <div style="padding:14px;">
                            <div style="font-size:.72rem; color:#a78bfa; margin-bottom:6px;">
                                {mtype_icon} {mtype.upper()}
                            </div>
                            <p style="font-size:.82rem; color:#9ca3af; height:44px; overflow:hidden; margin:0 0 10px;">
                                {cap}
                            </p>
                            <div style="display:flex; justify-content:space-between; font-size:.82rem; color:#6b7280;">
                                <span>❤️ {likes:,}</span>
                                <span>💬 {comms:,}</span>
                            </div>
                        </div>
                    </div>""", unsafe_allow_html=True)
    except Exception as ge:
        st.warning(f"Grid fetch failed: {ge}")
        _log(f"Grid telemetry error: {ge}", "warn")

st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab_metrics, tab_publish, tab_engage = st.tabs([
    "📈  Performance Metrics",
    "🚀  Enterprise Publisher",
    "🤖  Engagement Engine",
])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1  —  PERFORMANCE METRICS
# ════════════════════════════════════════════════════════════════════════════
with tab_metrics:
    st.markdown('<h2 class="gradient-header">Performance Metrics</h2>', unsafe_allow_html=True)
    st.markdown("<p style='color:#6b7280;margin-bottom:22px;'>Live growth acceleration analytics and engagement trend lines.</p>",
                unsafe_allow_html=True)

    snapshots = _active_query(AnalyticsSnapshot).order_by(AnalyticsSnapshot.timestamp.asc()).all()
    if snapshots:
        chart_df = pd.DataFrame([{
            "Date": s.timestamp.strftime("%Y-%m-%d"),
            "Followers": s.followers,
            "Following": s.following,
            "Engagement Rate": getattr(s, "engagement_rate", round(random.uniform(4.5, 7.2), 2)),
        } for s in snapshots])
    else:
        base  = profile["followers"]
        today = datetime.utcnow()
        rows  = [{
            "Date": (today - timedelta(days=i)).strftime("%Y-%m-%d"),
            "Followers": max(0, base - int(i * random.uniform(8, 22))),
            "Following": profile["following"] - int(i * random.uniform(1, 4)),
            "Engagement Rate": round(random.uniform(3.5, 7.8), 2),
        } for i in range(30, 0, -1)]
        rows.append({"Date": today.strftime("%Y-%m-%d"), "Followers": base,
                     "Following": profile["following"], "Engagement Rate": round(random.uniform(4.5, 7.2), 2)})
        chart_df = pd.DataFrame(rows)

    col_g1, col_g2 = st.columns(2)
    _chart_defaults = dict(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           font_color="#9ca3af", margin=dict(l=0, r=0, t=10, b=0), height=260)
    with col_g1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 👥 Follower Trajectory")
        fig1 = px.area(chart_df, x="Date", y="Followers", color_discrete_sequence=["#8B5CF6"])
        fig1.update_traces(line=dict(width=2.5), fillcolor="rgba(139,92,246,.1)")
        fig1.update_layout(**_chart_defaults, xaxis=dict(showgrid=False), yaxis=dict(gridcolor="rgba(255,255,255,.05)"))
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_g2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### ⚡ Engagement Rate Trend")
        fig2 = px.line(chart_df, x="Date", y="Engagement Rate", color_discrete_sequence=["#06B6D4"])
        fig2.update_traces(line=dict(width=2.5))
        fig2.update_layout(**_chart_defaults, showlegend=False, xaxis=dict(showgrid=False),
                           yaxis=dict(gridcolor="rgba(255,255,255,.05)"))
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### 🚀 Follower Growth Acceleration (Day-over-Day Δ)")
    cdf = chart_df.sort_values("Date").reset_index(drop=True)
    cdf["Growth Δ"] = cdf["Followers"].diff().fillna(0).astype(int)
    fig3 = go.Figure(go.Bar(
        x=cdf["Date"], y=cdf["Growth Δ"],
        marker_color=["#10b981" if v >= 0 else "#ef4444" for v in cdf["Growth Δ"]],
        marker_line_width=0,
    ))
    fig3.update_layout(**{**_chart_defaults, "height": 220}, bargap=0.3,
                       xaxis=dict(showgrid=False), yaxis=dict(gridcolor="rgba(255,255,255,.05)"))
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 2  —  ENTERPRISE PUBLISHER
# ════════════════════════════════════════════════════════════════════════════
with tab_publish:
    st.markdown('<h2 class="gradient-header">Enterprise Publishing Engine</h2>', unsafe_allow_html=True)
    st.markdown("<p style='color:#6b7280;margin-bottom:22px;'>Single Photo · Carousel · Reels — GPT-4o captions → direct instagrapi upload.</p>",
                unsafe_allow_html=True)

    col_edit, col_queue = st.columns([3, 2])

    with col_edit:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 📁 Media Format Selection")

        media_format = st.radio(
            "Post format",
            ["📷  Single Photo", "🎠  Carousel (Multi-Image)", "🎬  Instagram Reel"],
            horizontal=True,
            label_visibility="collapsed",
        )

        # Explain active format
        fmt_help = {
            "📷  Single Photo":           "Uploads via `client.photo_upload()` — JPG/PNG, max 1080×1350px.",
            "🎠  Carousel (Multi-Image)": "Uploads via `client.album_upload()` — 2-10 images in a single swipeable post.",
            "🎬  Instagram Reel":         "Uploads via `client.clip_upload()` — MP4 video, optional cover thumbnail.",
        }
        st.markdown(f"<p style='font-size:.82rem;color:#6b7280;margin-bottom:16px;'>ℹ️ {fmt_help[media_format]}</p>",
                    unsafe_allow_html=True)
        st.divider()

        # ── Caption generator ──
        st.markdown("#### ✍️ GPT-4o Caption Generator")
        topic_input = st.text_input("Post Topic", placeholder="e.g. 'acoustic panels for office fit-outs', 'cyber security for SMEs'")
        language_options = ["English", "Albanian", "German", "Serbian", "Auto-detect from topic and audience"]
        selected_language = st.selectbox(
            "Post Language",
            language_options,
            index=language_options.index(st.session_state.draft_language)
            if st.session_state.draft_language in language_options else 0,
        )
        if st.button("🤖  Generate Caption & Hashtags"):
            if not topic_input.strip():
                st.error("Enter a topic first.")
            else:
                with st.spinner("GPT-4o is crafting your caption…"):
                    gen = agent.generate_caption(topic_input.strip(), language=selected_language)
                    st.session_state.draft_caption  = gen.get("caption",      "")
                    st.session_state.draft_hashtags = gen.get("hashtags",     "")
                    st.session_state.draft_media    = gen.get("media_prompt", "")
                    st.session_state.draft_language = gen.get("language", selected_language)
                    st.session_state.draft_image_style = gen.get("image_style", "text")
                    _log(f"Caption generated for topic: {topic_input[:40]} ({st.session_state.draft_language})", "ok")

        caption_val  = st.text_area("Caption",    value=st.session_state.draft_caption,  height=130)
        hashtags_val = st.text_input("Hashtags",  value=st.session_state.draft_hashtags)
        media_prompt = st.text_area("Visual/Media Prompt", value=st.session_state.draft_media, height=80)
        st.caption(f"Generated image style: {st.session_state.draft_image_style}")

        st.divider()

        # ── Format-specific uploader ──
        if media_format == "📷  Single Photo":
            up_single = st.file_uploader(
                "Upload Photo (leave empty -> auto-generate AI image)",
                type=["jpg", "jpeg", "png"], accept_multiple_files=False,
            )
            image_source = st.radio(
                "Auto image style",
                ["Follow AI recommendation", "Designed text card", "Pure topic photo", "Topic web photo + overlay"],
                horizontal=True,
                help="Used only when no photo is uploaded.",
            )
            up_carousel, up_reel, up_thumb = None, None, None

        elif media_format == "🎠  Carousel (Multi-Image)":
            up_carousel = st.file_uploader(
                "Upload 2–10 images (order = upload order)",
                type=["jpg", "jpeg", "png"], accept_multiple_files=True,
            )
            if up_carousel:
                st.caption(f"🖼️ {len(up_carousel)} image(s) selected")
            up_single, up_reel, up_thumb, image_source = None, None, None, "Designed text card"

        else:  # Reel
            up_reel = st.file_uploader("Upload Reel (.mp4)", type=["mp4"], accept_multiple_files=False)
            up_thumb = st.file_uploader("Upload Cover Thumbnail (optional, JPG/PNG)", type=["jpg","jpeg","png"])
            up_single, up_carousel, image_source = None, None, "Designed text card"

        st.divider()
        st.markdown("#### 📅 Schedule Configuration")
        c_date, c_time = st.columns(2)
        sched_date = c_date.date_input("Target Date", min_value=datetime.today())
        sched_time = c_time.time_input("Target Time", value=datetime.now().time())

        # ── Dispatch mode ──
        st.markdown("#### ⚙️ Dispatch Mode")
        dispatch_mode = st.radio(
            "dispatch",
            ["🚀  Publish Instantly Live", "📋  Add to AI Autonomous Schedule Matrix"],
            horizontal=True, label_visibility="collapsed",
        )

        pub_col, sched_col = st.columns(2)
        publish_btn  = pub_col.button("🚀  Execute")
        schedule_btn = sched_col.button("📋  Queue")

        # ────────────────────────────────────────────────────────────────
        def _save_files_single(uf) -> str:
            if uf:
                ext  = Path(uf.name).suffix
                path = f"media/single_{int(datetime.utcnow().timestamp())}{ext}"
                with open(path, "wb") as fh: fh.write(uf.getbuffer())
            else:
                path = f"media/auto_gen_{int(datetime.utcnow().timestamp())}.png"
                visual_mode = st.session_state.draft_image_style
                if image_source == "Designed text card":
                    visual_mode = "text"
                elif image_source == "Pure topic photo":
                    visual_mode = "photo"
                use_photo = image_source.startswith("Topic web photo") or visual_mode == "photo"
                create_gradient_post_image(
                    topic_input,
                    caption_val or "AURA AI Post",
                    path,
                    visual_prompt=media_prompt,
                    use_web_photo=use_photo,
                    visual_mode=visual_mode,
                )
            return path

        def _save_files_carousel(ufs) -> list:
            paths = []
            for i, uf in enumerate(ufs):
                ext  = Path(uf.name).suffix
                path = f"media/carousel_{int(datetime.utcnow().timestamp())}_{i}{ext}"
                with open(path, "wb") as fh: fh.write(uf.getbuffer())
                paths.append(path)
            return paths

        def _save_reel(uf_vid, uf_thumb) -> tuple:
            vid_path   = f"media/reel_{int(datetime.utcnow().timestamp())}.mp4"
            thumb_path = None
            with open(vid_path, "wb") as fh: fh.write(uf_vid.getbuffer())
            if uf_thumb:
                thumb_path = f"media/reel_thumb_{int(datetime.utcnow().timestamp())}.jpg"
                with open(thumb_path, "wb") as fh: fh.write(uf_thumb.getbuffer())
            return vid_path, thumb_path

        # ── PUBLISH NOW ─────────────────────────────────────────────────
        if publish_btn or (dispatch_mode == "🚀  Publish Instantly Live" and schedule_btn):
            if not caption_val.strip():
                st.error("Caption is required.")
            elif not _require_verified_account("publishing", write_action=True):
                st.stop()
            else:
                with st.spinner("Uploading to Instagram…"):
                    try:
                        full_cap = f"{caption_val}\n\n{hashtags_val}".strip()
                        media_id = None

                        if media_format == "📷  Single Photo":
                            path = _save_files_single(up_single)
                            if st.session_state.is_sandbox:
                                media_id = ig_client.post_photo(path, full_cap)
                            else:
                                from pathlib import Path as PL
                                media   = ig_client.photo_upload(PL(path), caption=full_cap)
                                media_id = str(media.pk)
                            _log(f"Single photo published. ID: {media_id}", "ok")

                        elif media_format == "🎠  Carousel (Multi-Image)":
                            if not up_carousel or len(up_carousel) < 2:
                                st.error("Select at least 2 images for a carousel post.")
                                st.stop()
                            paths = _save_files_carousel(up_carousel)
                            if st.session_state.is_sandbox:
                                media_id = ig_client.post_photo(paths[0], full_cap)
                            else:
                                from pathlib import Path as PL
                                media   = ig_client.album_upload([PL(p) for p in paths], caption=full_cap)
                                media_id = str(media.pk)
                            _log(f"Carousel ({len(paths)} imgs) published. ID: {media_id}", "ok")

                        else:  # Reel
                            if not up_reel:
                                st.error("Upload an MP4 file for the Reel.")
                                st.stop()
                            vid_path, thumb_path = _save_reel(up_reel, up_thumb)
                            if st.session_state.is_sandbox:
                                media_id = ig_client.post_reel(vid_path, full_cap)
                            else:
                                from pathlib import Path as PL
                                kwargs   = {"caption": full_cap}
                                if thumb_path:
                                    kwargs["thumbnail"] = PL(thumb_path)
                                media   = ig_client.clip_upload(PL(vid_path), **kwargs)
                                media_id = str(media.pk)
                            _log(f"Reel published. ID: {media_id}", "ok")

                        db.add(Post(
                            account_id  = _active_account_id(),
                            caption    = caption_val,
                            media_type = "video" if media_format.startswith("🎬") else "image",
                            timestamp  = datetime.utcnow()
                        ))
                        db.commit()
                        st.success(f"✅ Published! Media ID: `{media_id}`")
                        st.balloons()
                    except Exception as pub_err:
                        st.error(f"Publish failed: {pub_err}")
                        _log(f"Publish error: {pub_err}", "error")

        # ── SCHEDULE (Add to Autonomous Matrix) ─────────────────────────
        elif dispatch_mode == "📋  Add to AI Autonomous Schedule Matrix" and schedule_btn:
            if not caption_val.strip():
                st.error("Caption is required.")
            elif not _require_verified_account("scheduling"):
                st.stop()
            else:
                target_dt = datetime.combine(sched_date, sched_time)
                db.add(ScheduledPost(
                    account_id   = _active_account_id(),
                    caption      = caption_val,
                    media_type   = "video" if media_format.startswith("🎬") else "image",
                    status       = "scheduled",
                    timestamp    = target_dt,
                ))
                db.commit()
                st.success(f"✅ Queued in Autonomous Matrix for {target_dt.strftime('%Y-%m-%d %H:%M UTC')}")
                _log(f"Post queued → {target_dt.strftime('%m-%d %H:%M')}", "info")
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Pipeline queue panel ─────────────────────────────────────────────────
    with col_queue:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 🗓️ Autonomous Schedule Matrix")

        pipeline = (_active_query(ScheduledPost).filter(ScheduledPost.status == "scheduled")
                    .order_by(ScheduledPost.timestamp.asc()).all())

        if not pipeline:
            st.info("Matrix is empty — no queued posts.")
        else:
            for item in pipeline:
                sched_str = item.timestamp.strftime("%m-%d %H:%M UTC") if item.timestamp else "—"
                fmt_icon = "🎬" if item.media_type == "video" else "🖼️"
                st.markdown(f"""
                <div style="padding:14px;border-radius:10px;border:1px solid rgba(255,255,255,.06);
                            background:rgba(255,255,255,.02);margin-bottom:12px;">
                    <strong style="color:#a78bfa;">⏱ {sched_str}</strong>
                    <span style="float:right;font-size:.72rem;color:#6b7280;">{fmt_icon}</span><br>
                    <p style="font-size:.82rem;color:#d1d5db;margin:6px 0;height:34px;overflow:hidden;">
                        {item.caption[:110]}…
                    </p>
                </div>""", unsafe_allow_html=True)
                if st.button("🗑 Cancel", key=f"del_{item.id}"):
                    db.delete(item); db.commit()
                    st.success("Removed from matrix."); st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### ✅ Recently Published")
        recent_posted = (_active_query(Post).order_by(Post.timestamp.desc()).limit(6).all())
        if not recent_posted:
            st.info("No posts published via AURA yet.")
        else:
            for rp in recent_posted:
                when = rp.timestamp.strftime("%m-%d %H:%M") if rp.timestamp else "—"
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;padding:9px 0;
                            border-bottom:1px solid rgba(255,255,255,.04);font-size:.82rem;">
                    <span style="color:#d1d5db;max-width:76%;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;">
                        {rp.caption[:68]}
                    </span>
                    <span style="color:#6b7280;flex-shrink:0;margin-left:8px;">{when}</span>
                </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 3  —  ENGAGEMENT ENGINE
# ════════════════════════════════════════════════════════════════════════════
with tab_engage:
    st.markdown('<h2 class="gradient-header">Advanced Engagement Engine</h2>', unsafe_allow_html=True)
    st.markdown("<p style='color:#6b7280;margin-bottom:22px;'>Dual-mode inbox · Autopilot Rulebook · Scan &amp; Execute auto-replies.</p>",
                unsafe_allow_html=True)

    # ── Autopilot Rulebook panel ─────────────────────────────────────────────
    with st.expander("⚙️  Auto-Pilot Trigger Rulebook", expanded=False):
        st.markdown("""
        <p style='font-size:.85rem;color:#9ca3af;margin-bottom:16px;'>
        Define keyword triggers and response templates. When the <strong>Scan & Execute</strong> engine runs,
        it checks each unread DM / comment against active rules (in order) before falling back to GPT-4o.
        Use <code>{username}</code> as a placeholder for the sender's handle.
        </p>""", unsafe_allow_html=True)

        existing_rules = _active_query(AutopilotRule).order_by(AutopilotRule.id.asc()).all()

        # Show existing rules
        for rule in existing_rules:
            with st.container():
                rc1, rc2, rc3, rc4, rc5 = st.columns([2, 1, 3, 4, 1])
                new_name  = rc1.text_input("Rule Name",        value=rule.name,              key=f"rname_{rule.id}")
                new_scope = rc2.selectbox("Scope",             ["both","dm","comment"],
                                          index=["both","dm","comment"].index(rule.scope),   key=f"rscope_{rule.id}")
                new_kw    = rc3.text_input("Keywords (comma)", value=rule.keyword,            key=f"rkw_{rule.id}")
                new_tpl   = rc4.text_input("Response Template",value=rule.response_template, key=f"rtpl_{rule.id}")
                new_act   = rc5.checkbox("On",                 value=rule.active,             key=f"ract_{rule.id}")

                rb1, rb2 = st.columns([1, 1])
                if rb1.button("💾 Save Rule", key=f"rsave_{rule.id}"):
                    rule.name = new_name; rule.scope = new_scope; rule.keyword = new_kw
                    rule.response_template = new_tpl; rule.active = new_act
                    db.commit()
                    st.success("Rule saved."); _log(f"Rule '{new_name}' updated.", "info"); st.rerun()
                if rb2.button("🗑 Delete", key=f"rdel_{rule.id}"):
                    db.delete(rule); db.commit()
                    _log(f"Rule '{rule.name}' deleted.", "warn"); st.rerun()
                st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,.04);margin:8px 0;'>",
                            unsafe_allow_html=True)

        # Add new rule form
        st.markdown("#### ➕ Add New Rule")
        na1, na2, na3, na4 = st.columns([2, 1, 3, 4])
        nr_name  = na1.text_input("Name",    placeholder="Rule name",         key="nr_name")
        nr_scope = na2.selectbox("Scope",    ["both","dm","comment"],          key="nr_scope")
        nr_kw    = na3.text_input("Keywords", placeholder="keyword1, keyword2",key="nr_kw")
        nr_tpl   = na4.text_input("Template", placeholder="Hey {username}! ...",key="nr_tpl")

        if st.button("✅  Add Rule", use_container_width=False):
            if not nr_name.strip() or not nr_kw.strip() or not nr_tpl.strip():
                st.error("All fields are required.")
            else:
                db.add(AutopilotRule(
                    account_id=_active_account_id(),
                    name=nr_name.strip(), scope=nr_scope,
                    keyword=nr_kw.strip(), response_template=nr_tpl.strip(),
                ))
                db.commit()
                st.success(f"Rule '{nr_name}' added!")
                _log(f"New autopilot rule added: '{nr_name}'", "ok")
                st.rerun()

    st.divider()

    # ── Scan & Execute ───────────────────────────────────────────────────────
    sc1, sc2 = st.columns([2, 5])
    with sc1:
        st.markdown('<div class="scan-btn">', unsafe_allow_html=True)
        run_scan = st.button("🔍  Scan & Execute Auto-Replies", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with sc2:
        st.markdown("""
        <p style='font-size:.83rem;color:#6b7280;padding-top:12px;'>
        Downloads all unread DMs + comments on your last 5 posts. Matches rules, then GPT-4o for
        everything else. Pushes replies and logs every action to the audit trail.
        </p>""", unsafe_allow_html=True)

    if run_scan:
        if not _require_verified_account("running autopilot scan"):
            st.stop()
        rules = _active_query(AutopilotRule).filter(AutopilotRule.active == True).all()
        _log("Autopilot scan started…", "info")
        with st.spinner("Scanning DMs and post comments…"):
            try:
                summary = run_autopilot_scan(ig_client, rules, strategy)
                st.success(
                    f"✅ Scan complete — {summary['dm_replied']} DMs replied, "
                    f"{summary['comment_replied']} comments replied."
                )
                if summary["errors"]:
                    for err in summary["errors"]:
                        st.warning(f"⚠ {err}")
                _log(f"Scan done: {summary['dm_replied']} DMs, {summary['comment_replied']} comments.", "ok")
            except Exception as scan_err:
                _mark_account_error(scan_err, "Autopilot scan")
                st.error(f"Scan failed: {scan_err}")
                _log(f"Scan crashed: {scan_err}", "error")

    st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

    # ── Dual-mode inbox ──────────────────────────────────────────────────────
    engage_mode = st.radio("View", ["✉️  Direct Messages", "💬  Post Comment Threads"],
                           horizontal=True, label_visibility="collapsed")

    # ── DM MODE ─────────────────────────────────────────────────────────────
    if engage_mode == "✉️  Direct Messages":
        col_dm_l, col_dm_r = st.columns([1, 1])

        with col_dm_l:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### ✉️ Unread Direct Message Threads")
            try:
                dms    = _get_direct_messages(ig_client)
                unread = [d for d in dms if d.get("is_unread")]

                if not unread:
                    st.info("No unread DMs at this time.")
                else:
                    for dm in unread:
                        ts    = (dm.get("timestamp") or "")[:16].replace("T", " ")
                        uname = dm.get("username", "unknown")
                        text  = dm.get("text", "")
                        st.markdown(f"""
                        <div style="padding:14px;border-radius:10px;border:1px solid rgba(255,255,255,.06);
                                    background:rgba(255,255,255,.02);margin-bottom:12px;">
                            <strong style="color:#06b6d4;">@{uname}</strong>
                            <span style="float:right;font-size:.75rem;color:#6b7280;">{ts}</span><br>
                            <p style="margin:8px 0;font-size:.88rem;">"{text}"</p>
                        </div>""", unsafe_allow_html=True)

                        ck = f"dm_draft_{dm['id']}"
                        if ck not in st.session_state:
                            st.session_state[ck] = agent.generate_dm_reply(text, uname)

                        draft = st.text_area("AI Draft", value=st.session_state[ck],
                                             key=f"dm_ta_{dm['id']}", height=90)

                        bc1, bc2 = st.columns(2)
                        if bc1.button("✅ Send", key=f"dm_send_{dm['id']}"):
                            try:
                                if not _require_verified_account("sending a DM reply", write_action=True):
                                    st.stop()
                                ok = _reply_to_direct_message(ig_client, dm["id"], draft)
                                if ok:
                                    db.add(EngagementLog(account_id=_active_account_id(), type="dm", username=uname,
                                                         message_id=dm["id"], input_text=text,
                                                         response_text=draft, status="sent", autopilot=False))
                                    db.commit()
                                    _log(f"Manual DM reply sent → @{uname}", "ok")
                                    st.success("Sent!"); st.rerun()
                            except Exception as se:
                                _mark_account_error(se, "Manual DM send")
                                st.error(f"Failed: {se}"); _log(f"DM send err: {se}", "error")

                        if bc2.button("🔄 Regen", key=f"dm_regen_{dm['id']}"):
                            st.session_state[ck] = agent.generate_dm_reply(text, uname)
                            st.rerun()

            except Exception as de:
                st.error(f"Could not load DMs: {de}"); _log(f"DM load err: {de}", "error")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_dm_r:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### 📊 DM Engagement Stats")
            dm_logs = (_active_query(EngagementLog).filter(EngagementLog.type == "dm")
                       .order_by(EngagementLog.responded_at.desc()).limit(20).all())
            if not dm_logs:
                st.info("No DM responses logged yet.")
            else:
                auto_count   = sum(1 for l in dm_logs if l.autopilot)
                manual_count = len(dm_logs) - auto_count
                fig_dm = go.Figure(go.Pie(
                    labels=["Autopilot", "Manual"],
                    values=[auto_count, manual_count],
                    hole=.55,
                    marker_colors=["#10b981", "#6366f1"],
                ))
                fig_dm.update_layout(showlegend=True, paper_bgcolor="rgba(0,0,0,0)",
                                     font_color="#9ca3af", height=200,
                                     margin=dict(l=0, r=0, t=10, b=0))
                st.plotly_chart(fig_dm, use_container_width=True)

                st.markdown("**Recent DM Log**")
                for l in dm_logs[:8]:
                    when = l.responded_at.strftime("%m-%d %H:%M") if l.responded_at else "—"
                    ap   = "🤖" if l.autopilot else "👤"
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;padding:8px 0;
                                border-bottom:1px solid rgba(255,255,255,.04);font-size:.8rem;">
                        <span style="color:#d1d5db;">{ap} @{l.username}: {(l.input_text or '')[:40]}…</span>
                        <span style="color:#6b7280;flex-shrink:0;margin-left:8px;">{when}</span>
                    </div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # ── COMMENT MODE ─────────────────────────────────────────────────────────
    else:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 💬 Post Comment Threads (Last 5 Posts)")
        try:
            all_posts = _get_recent_posts(ig_client, limit=5)
            if not all_posts:
                st.info("No posts found.")
            else:
                post_selector = {
                    f"Post {i+1}: {(p.get('caption') or '')[:50]}…": p
                    for i, p in enumerate(all_posts)
                }
                chosen_label = st.selectbox("Select post to inspect", list(post_selector.keys()))
                chosen_post  = post_selector[chosen_label]
                pid          = chosen_post.get("id", "")

                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;padding:10px 0;
                            font-size:.82rem;color:#9ca3af;">
                    <span>❤️ {chosen_post.get('like_count',0):,} likes</span>
                    <span>💬 {chosen_post.get('comment_count',0):,} comments</span>
                    <span>🆔 {pid}</span>
                </div>""", unsafe_allow_html=True)
                st.divider()

                comments = _get_comments(ig_client, pid)
                unread_c = [c for c in comments if c.get("is_unread")]

                if not unread_c:
                    st.info("No unread comments on this post.")
                else:
                    for comm in unread_c:
                        cid   = comm.get("id","")
                        uname = comm.get("username","user")
                        text  = comm.get("text","")

                        st.markdown(f"""
                        <div style="padding:14px;border-radius:10px;border:1px solid rgba(255,255,255,.06);
                                    background:rgba(255,255,255,.02);margin-bottom:12px;">
                            <strong style="color:#a78bfa;">@{uname}</strong><br>
                            <p style="margin:8px 0;font-size:.88rem;">"{text}"</p>
                        </div>""", unsafe_allow_html=True)

                        ck = f"comm_draft_{cid}"
                        if ck not in st.session_state:
                            st.session_state[ck] = agent.generate_comment_reply(text, uname)

                        draft = st.text_area("AI Draft Reply", value=st.session_state[ck],
                                             key=f"comm_ta_{cid}", height=80)

                        if st.button("✅ Post Comment Reply", key=f"comm_send_{cid}"):
                            try:
                                if not _require_verified_account("posting a comment reply", write_action=True):
                                    st.stop()
                                ok = _reply_to_comment(ig_client, pid, str(cid), draft)
                                if ok:
                                    db.add(EngagementLog(account_id=_active_account_id(), type="comment", username=uname,
                                                         message_id=str(cid), input_text=text,
                                                         response_text=draft, status="sent", autopilot=False))
                                    db.commit()
                                    _log(f"Comment reply posted → @{uname}", "ok")
                                    st.success("Reply posted!"); st.rerun()
                            except Exception as ce:
                                _mark_account_error(ce, "Manual comment send")
                                st.error(f"Failed: {ce}"); _log(f"Comment reply err: {ce}", "error")

        except Exception as pe:
            st.error(f"Could not load posts/comments: {pe}"); _log(f"Comment load err: {pe}", "error")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Engagement Audit Log ─────────────────────────────────────────────────
    st.markdown("#### 📊 Full Engagement Audit Log")
    st.markdown('<div class="glass-card" style="padding:20px 24px;">', unsafe_allow_html=True)
    logs = (_active_query(EngagementLog).order_by(EngagementLog.responded_at.desc()).limit(20).all())
    if not logs:
        st.info("No engagement events recorded yet.")
    else:
        log_data = [{
            "Date (UTC)":   l.responded_at.strftime("%Y-%m-%d %H:%M:%S") if l.responded_at else "—",
            "Type":         l.type.upper(),
            "Source":       "🤖 Auto" if l.autopilot else "👤 Manual",
            "Username":     f"@{l.username}",
            "Incoming":     (l.input_text    or "")[:80],
            "AI Response":  (l.response_text or "")[:80],
            "Status":       l.status,
        } for l in logs]
        st.dataframe(pd.DataFrame(log_data), use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# CLEANUP
# ─────────────────────────────────────────────────────────────────────────────
db.close()
